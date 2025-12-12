import requests
import re
import json
from bs4 import BeautifulSoup
import execjs


def execute_js_iife(js_code: str) -> dict:
    """执行 JS IIFE 并返回结果"""
    # 包装代码，让 IIFE 的返回值赋给变量
    wrapped_code = f"var result = {js_code};"

    # 使用 execjs 执行
    ctx = execjs.compile(wrapped_code)
    return ctx.eval("result")


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.dongqiudi.com/",
}

response = requests.get("https://www.dongqiudi.com/live/70", timeout=5, headers=headers)
response.raise_for_status()
html = response.text
soup = BeautifulSoup(html, "html.parser")

# 方式1: 从 script 标签提取
scripts = soup.find_all("script")
script_texts = [s.get_text() for s in scripts]
nuxt_script_text = next((s for s in script_texts if "window.__NUXT__" in s), None)

if not nuxt_script_text:
    raise ValueError("未找到包含 window.__NUXT__ 的 script 标签")

start = nuxt_script_text.find("(function")
if start < 0:
    raise ValueError("未找到 IIFE 代码")

js_code = nuxt_script_text[start:]

print("正在执行 JS 代码...")
result = execute_js_iife(js_code)

data = result.get("data", [])
result = []
for item in data[-1]["matchListData"].values():
    for sub_item in item:
        if sub_item.get("relate_type") == "match":
            result.append(
                {
                    "match_id": sub_item.get("match_id"),
                    "team_A_id": sub_item.get("team_A_id"),
                    "team_A_name": sub_item.get("team_A_name"),
                    "team_B_id": sub_item.get("team_B_id"),
                    "team_B_name": sub_item.get("team_B_name"),
                    "competition_name": sub_item.get("competition_name"),
                    "competition_id": sub_item.get("competition_id"),
                }
            )

print(result)

# print([match for match in match_list if match.get("relate_type", "") == "match"])
# # 打印结果
# print("\n执行结果:")
# print(json.dumps(result, indent=2, ensure_ascii=False))  # 只打印前1000字符
