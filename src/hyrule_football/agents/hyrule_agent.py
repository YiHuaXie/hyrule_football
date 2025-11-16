# from langchain.agents import AgentExecutor, create_tool_calling_agent, create_structured_chat_agent
# from langchain_deepseek import ChatDeepSeek
# from langchain_core.runnables import ConfigurableField

from dotenv import load_dotenv
from hyrule_football.services import get_hot_match_list

load_dotenv()


class HyruleAgent:

    def __init__(self):
        pass

    def run_agent(self, message_text: str, user_id: str) -> dict:
        matche_list = get_hot_match_list()
        return {"output": "\n".join(m.match_description for m in matche_list)}
