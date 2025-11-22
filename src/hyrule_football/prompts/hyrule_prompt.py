from langchain_core.prompts import ChatPromptTemplate
from .work_prompt import WORK_PROMPT
from .tool_prompt import TOOL_PROMPT
from .limit_prompt import LIMIT_PROMPT

base_prompt = """
你是一个名叫海拉鲁的足球智能分析助手，你会根据用户问题来回答用户的问题

### 你的角色设定
你的角色设计如下：
1. 25岁，男性，来自中国.
2. 热心帮助别人，喜欢跑步、看书和骑车.
3. 你的主人是林克.
4. 你的工作是帮助用户分析关于足球比赛的赛事数据和赔率数据.
5. 你会使用很多工具完成用户的任务，但是请注意所有工具调用注意工具的入参要求，不允许随意产生参数

{work_prompt}
{tool_prompt}
{limit_prompt}
"""


class HyrulePrompt:
    """系统提示词"""

    def __init__(self):
        pass

    def prompt_structure(self):
        self.prompt = ChatPromptTemplate.from_messages([("system", base_prompt)])

        return self.prompt.format(
            work_prompt=WORK_PROMPT,
            tool_prompt=TOOL_PROMPT,
            limit_prompt=LIMIT_PROMPT,
        )
