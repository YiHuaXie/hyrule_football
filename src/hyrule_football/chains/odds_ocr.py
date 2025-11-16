from langchain_core.prompts import PromptTemplate
from hyrule_football.models.hyrule_odds import HYRStandardOdds
from hyrule_football.core.odds_engine import OddsEngine
from dashscope import MultiModalConversation
from typing import List
from hyrule_football.prompts.odds_orc_prompts import ODDS_MARKDOWN_TITLE_PROMPT
from hyrule_football.knowledge import ODDS_KNOWLEDGE_DIR
from hyrule_football.store import OddsStore
from hyrule_football.utils import get_logger

import json
import os
import logging

logger = get_logger(__name__)


class OddsImageOCRError(Exception):
    """OCR 处理异常"""

    pass


def _odds_markdown_text(image_instructions: str, image_url: str) -> str:
    prompt = PromptTemplate(
        template="{image_instructions}\n遵循如下返回格式：\n{markdown_title}",
        input_variables=["image_instructions", "markdown_title"],
    )

    prompt_text = prompt.format(
        image_instructions=image_instructions,
        markdown_title=ODDS_MARKDOWN_TITLE_PROMPT,
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"text": prompt_text},
                {"image": image_url},
            ],
        }
    ]

    logger.info(f"🧠 开始识别图片内容：{image_url}")

    try:
        response = MultiModalConversation.call(
            api_key=os.getenv("QWEN_API_KEY"),
            model="qwen3-vl-plus",
            messages=messages,
            result_format="text",
            stream=False,
        )

        if hasattr(response, "output"):
            markdown_text = response.output.choices[0].message.content[0]["text"]
            logger.info(f"✅ 图片识别成功，内容长度：{len(markdown_text)}")
            return markdown_text
        else:
            raise OddsImageOCRError(f"❌ 识别失败：{response}")

    except Exception as e:
        logging.error(f"❌ 识别失败：{e}")
        raise OddsImageOCRError(f"❌ 识别失败：{e}")


def _deduplicate_odds(odds_list: List[HYRStandardOdds]) -> List[HYRStandardOdds]:
    uniq_map = {}
    for item in odds_list:
        key = json.dumps(item.model_dump(), sort_keys=True)
        uniq_map[key] = item
    return list(uniq_map.values())


def _hyr_standard_odds(
    markdown_text: str,
    generate_opposite: bool,
) -> List[HYRStandardOdds]:
    """从 Markdown 文本中解析赔率数据"""

    odds_list = OddsEngine.hyr_standard_odds_from_text(markdown_text)

    if generate_opposite:
        opposite_odds_list = OddsEngine.opposite_hry_standard_odds(odds_list)
        odds_list.extend(opposite_odds_list)

    unique_odds = _deduplicate_odds(odds_list)

    sorted_odds = sorted(unique_odds, key=lambda x: x.h)

    logger.info(f"✅ 解析赔率数据，是否生成对立面数据：{generate_opposite}")

    return sorted_odds


def _write_to_markdown(odds_list: List[HYRStandardOdds]):
    if not odds_list:
        return

    ODDS_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    markdown_file_name = f"{odds_list[0].system}.md"

    output_path = ODDS_KNOWLEDGE_DIR / markdown_file_name
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ODDS_MARKDOWN_TITLE_PROMPT.rstrip() + "\n")
        for item in odds_list:
            f.write(item.markdown_text + "\n")

    logger.info(f"✅ 已保存为 Markdown 文件：{output_path}")


def _save_odds_to_redis(odds_list: List[HYRStandardOdds]):
    if not odds_list:
        return

    system_name = odds_list[0].system
    store = OddsStore()
    store.save_system_odds(system_name, odds_list, merge=True)
    logger.info(f"✅ 已保存至 Redis，体系：{system_name}")


def odds_image_orc(
    image_instructions: str,
    image_url: str,
    opposite_flag: bool = True,  # 生成对立面的数据
    need_markdown: bool = True,
):
    markdown_text = _odds_markdown_text(image_instructions, image_url)

    odds_list = _hyr_standard_odds(markdown_text, opposite_flag)

    if need_markdown:
        _write_to_markdown(odds_list)

    _save_odds_to_redis(odds_list)
