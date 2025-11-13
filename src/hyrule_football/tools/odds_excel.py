"""赔率 Excel 的 相关处理"""

import os
from dotenv import load_dotenv
from dashscope import MultiModalConversation
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek


def recognize_excel_from_image(image_url: str, output_path: str) -> str:
    """调用通义千问多模态模型识别图片中的 Excel 内容，并返回 markdown 文本"""
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
