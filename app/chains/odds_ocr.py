from langchain_core.prompts import PromptTemplate
from app.core.odds_engine import OddsEngine
from dashscope import MultiModalConversation
from typing import List
from app.prompts.odds_orc_prompts import ODDS_MARKDOWN_TITLE_PROMPT
from bs4 import BeautifulSoup
from markdown import markdown
from app.store import get_odds_store
from app.utils import get_logger, opposite_water_level
from app.models import StandardOdds

import json
import os
import logging

logger = get_logger(__name__)


class OddsImageOCRError(Exception):
    """OCR 处理异常"""

    pass


def odds_markdown_text(image_instructions: str, image_url: str) -> str:
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


# def _hyr_standard_odds(
#     markdown_text: str,
#     generate_opposite: bool,
# ) -> List[HYRStandardOdds]:
#     """从 Markdown 文本中解析赔率数据"""

#     odds_list = OddsEngine.hyr_standard_odds_from_text(markdown_text)

#     if generate_opposite:
#         opposite_odds_list = OddsEngine.opposite_hry_standard_odds(odds_list)
#         odds_list.extend(opposite_odds_list)

#     unique_odds = _deduplicate_odds(odds_list)

#     sorted_odds = sorted(unique_odds, key=lambda x: x.h)

#     logger.info(f"✅ 解析赔率数据，是否生成对立面数据：{generate_opposite}")

#     return sorted_odds


# def _write_to_markdown(odds_list: List[HYRStandardOdds]):
#     if not odds_list:
#         return

#     ODDS_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

#     markdown_file_name = f"{odds_list[0].system}.md"

#     output_path = ODDS_KNOWLEDGE_DIR / markdown_file_name
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(ODDS_MARKDOWN_TITLE_PROMPT.rstrip() + "\n")
#         for item in odds_list:
#             f.write(item.markdown_text + "\n")

#     logger.info(f"✅ 已保存为 Markdown 文件：{output_path}")


# def _save_odds_to_redis(odds_list: List[HYRStandardOdds]):
#     if not odds_list:
#         return

#     system_name = odds_list[0].system
#     store = get_odds_store()
#     store.save_system_odds(system_name, odds_list, merge=True)
#     logger.info(f"✅ 已保存至 Redis，体系：{system_name}")


def generate_odds_list(markdown_path: str) -> None:
    """从 Markdown 文件中解析赔率数据"""

    if not os.path.exists(markdown_path):
        raise FileNotFoundError(f"❌ 文件不存在: {markdown_path}")

    with open(markdown_path, "r", encoding="utf-8") as f:
        md_text = f.read().strip()

    odds_list = _get_odds_list_from_markdown_text(md_text)
    odds_list.extend(_opposite_odds_list(odds_list))
    odds_list = _deduplicate_and_sort(odds_list)

    system_name = odds_list[0].system
    store = get_odds_store()
    store.save_system_odds(system_name, odds_list, merge=True)
    logger.info(f"✅ 已保存至 Redis，体系：{system_name}")


def _get_odds_list_from_markdown_text(markdown_text: str) -> List[StandardOdds]:
    # 解析 HTML
    html = markdown(markdown_text, extensions=["tables"])
    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("tr")
    if len(rows) < 2:
        return []

    headers = [th.get_text(strip=True) for th in rows[0].find_all(["td", "th"])]
    # 解析数据行
    odds_list = []
    for row in rows[1:]:
        values = [td.get_text(strip=True) for td in row.find_all("td")]
        # 转成 model
        row_dict = dict(zip(headers, values))
        odds = StandardOdds(**row_dict)
        odds_list.append(odds)

    return odds_list


def _opposite_odds_list(odds_list: List[StandardOdds]) -> List[StandardOdds]:
    """将 StandardOdds 列表中的转换为对立面数据"""
    new_list = []
    for odds in odds_list:
        goal_line = odds.goal_line * -1
        goal_line = 0.0 if goal_line == 0.0 else goal_line
        new_odds = StandardOdds(
            system=odds.system,
            interval=odds.interval,
            w=odds.l,
            d=odds.d,
            l=odds.w,
            return_rate=odds.return_rate,
            goal_line=goal_line,
            water_level=opposite_water_level(odds.water_level),
        )
        new_list.append(new_odds)

    return new_list


def _deduplicate_and_sort(odds_list: List[StandardOdds]) -> List[StandardOdds]:
    """去重并排序"""

    uniq_map = {}
    for item in odds_list:
        key = json.dumps(item.model_dump(), sort_keys=True)
        uniq_map[key] = item

    odds_list = list(uniq_map.values())
    odds_list = sorted(odds_list, key=lambda x: (x.w, x.d, x.l))
    return odds_list
