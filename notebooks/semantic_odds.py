# -*- coding: utf-8 -*-

import os
import re
from dotenv import load_dotenv
from dashscope import MultiModalConversation
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

load_dotenv()


def recognize_excel_from_image(image_url: str, output_path: str) -> str:
    """
    调用通义千问多模态模型识别图片中的 Excel 内容，并返回 markdown 文本
    """
    print(f"🧠 开始识别图片内容：{image_url}")

    messages = [
        {
            "role": "user",
            "content": [
                {"image": image_url},
                {
                    "text": """
                 识别图中的 Excel 的内容，生成对应的 markdown 表格文本
                 注意：
                 - 如果有不属于 excel 的元素请过滤，如水印，覆盖在 excel 的文字 表情等
                 - excel 中存在暂时无法识别的内容，请使用“ZSBNSB”填充单元格
                 """
                },
            ],
        }
    ]

    response = MultiModalConversation.call(
        api_key=os.getenv("QWEN_API_KEY"),
        model="qwen3-vl-plus",
        messages=messages,
        result_format="text",
        stream=False,
    )

    if hasattr(response, "output"):
        markdown_text = response.output.choices[0].message.content[0]["text"]
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print(f"✅ 图片识别完成，已保存为：{output_path}")
        return markdown_text
    else:
        raise RuntimeError(f"❌ 识别失败：{response}")


def semantic_transform(input_markdown: str, output_path: str):
    """
    使用 DeepSeek 对报表进行语义化
    """
    print(f"🧩 开始语义化处理：{input_markdown}")

    deepseek = ChatDeepSeek(
        model=os.getenv("DEEPSEEK_REASONER"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_template(
        """
你是一名竞彩足球标准赔率分析专家。
现在给你一份关于标准赔率的 markdown 内容，理解其中的数据，并生成一份自然语言化的报告。
要求：
- 输出为Markdown格式；
- 使用自然语言描述每个指标；
报表内容如下：
{markdown_content}
请输出语义化后的 Markdown 报告。
"""
    )

    chain = prompt | deepseek

    with open(input_markdown, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    if "ZSBNSB" in markdown_content:
        print(f"❌ 包含无法识别区域，跳过语义化处理")
        return

    lang_md = chain.invoke({"markdown_content": markdown_content}).content
    match = re.search(r"```(?:markdown|md)?\n(.*?)```", lang_md, re.DOTALL)
    if match:
        lang_md = match.group(1).strip()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(lang_md)
    print(f"✅ 语义化完成，已输出至：{output_path}")


def generate_semantic_report(
    image_url: str = None,
    file_name: str = "report",
    skip_ocr: bool = False,
    save_md: bool = True,
    docs_dir: str = "../docs",
) -> str:
    """
    主调用函数：识别Excel图片并生成语义化报表

    参数：
        image_url: Excel 图片URL
        file_name: 文件名（不含后缀）
        skip_ocr: 是否跳过图片识别
        save_md: 是否保留中间生成的Markdown文件
        docs_dir: 保存目录

    返回：
        语义化Markdown文件路径
    """

    os.makedirs(docs_dir, exist_ok=True)
    md_path = os.path.join(docs_dir, f"{file_name}.md")
    lang_path = os.path.join(docs_dir, f"{file_name}_lang.md")

    # 图片识别阶段
    if not skip_ocr:
        if not image_url:
            raise ValueError("❌ 缺少 image_url 参数")
        recognize_excel_from_image(image_url, md_path)
    else:
        if not os.path.exists(md_path):
            raise FileNotFoundError(f"❌ 找不到已存在的Markdown文件：{md_path}")
        print("⚙️ 已跳过图片识别阶段")

    # 语义化阶段
    semantic_transform(md_path, lang_path)

    # 删除中间Markdown文件（可选）
    if not save_md and os.path.exists(md_path):
        os.remove(md_path)
        print("🧹 已删除中间 Markdown 文件")

    print(f"\n🎯 全部流程完成 ✅\n输出文件：{lang_path}")
    return lang_path
