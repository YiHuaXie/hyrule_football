from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain_core.runnables import RunnableWithMessageHistory

from hyrule_football.config import settings
from hyrule_football.utils import get_logger
from hyrule_football.prompts.hyrule_prompt import HyrulePrompt
from hyrule_football.memory.chat_memory import ChatMemory

# from hyrule_football.tools import (
#     get_match_list,
#     get_match_for_team,
#     get_match_for_matchup,
#     get_odds_info_for_match,
#     plan_match_odds_query,
# )

logger = get_logger(__name__)

MCP_DIR = Path(__file__).parent / "../mcp/"
MATCH_MCP_SERVER = (MCP_DIR / "match_mcp.py").resolve()
ODDS_MCP_SERVER = (MCP_DIR / "odds_mcp.py").resolve()


class HyruleAgent:

    def __init__(self):
        print("HyruleAgent::__init__")
        print(settings.DEEPSEEK_CHAT)
        self.llm = ChatDeepSeek(
            model=settings.DEEPSEEK_CHAT,  # os.environ.get("DEEPSEEK_CHAT"),
            api_key=settings.DEEPSEEK_API_KEY,  # os.environ.get("DEEPSEEK_API_KEY"),
        )

        # self.tools = [
        #     get_match_list,
        #     get_match_for_team,
        #     get_match_for_matchup,
        #     get_odds_info_for_match,
        #     plan_match_odds_query,
        # ]

        self.prompt = HyrulePrompt().prompt_structure()
        self.chat_memory = ChatMemory()

        self.mcp_client = MultiServerMCPClient(
            {
                "match": {
                    "command": "python",
                    "args": [str(MATCH_MCP_SERVER)],
                    "transport": "stdio",
                },
                "odds": {
                    "command": "python",
                    "args": [str(ODDS_MCP_SERVER)],
                    "transport": "stdio",
                },
            }
        )

        # # 创建 Agent（单智能体）
        # self.agent = create_agent(
        #     model=self.llm,
        #     tools=self.tools,
        #     system_prompt=self.prompt,
        #     debug=True,
        # )

        # self.agent_with_memory = RunnableWithMessageHistory(
        #     self.agent,
        #     get_session_history=self.chat_memory.get_history,
        #     input_messages_key="messages",
        #     history_messages_key="messages",
        # )

    async def _create_agent(self):
        """创建 Agent"""
        tools = await self.mcp_client.get_tools()
        self.agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=self.prompt,
            debug=True,
        )

        # 包装 Memory
        self.agent_with_memory = RunnableWithMessageHistory(
            self.agent,
            get_session_history=self.chat_memory.get_history,
            input_messages_key="messages",
            history_messages_key="messages",
        )

    async def run_agent(self, message_text: str, user_id: str) -> str:
        try:
            if not hasattr(self, "agent"):
                await self._create_agent()

            history = self.agent_with_memory.get_session_history(user_id)
            history.add_user_message(message_text)

            result = await self.agent_with_memory.ainvoke(
                {},
                config={"configurable": {"session_id": user_id}},
            )
            messages = result["messages"]
            return messages[-1].content
        except Exception as e:
            logger.exception(f"Hyrule Agent Error: {e}")
            return "暂时不知道你在说什么"
