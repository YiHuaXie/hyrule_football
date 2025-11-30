from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain_core.runnables import RunnableWithMessageHistory

from hyrule_football.config import settings
from hyrule_football.utils import get_logger
from hyrule_football.prompts.hyrule_prompt import HyrulePrompt
from hyrule_football.memory.chat_memory import ChatMemory
from hyrule_football.mcp.mcp_client import mcp_client

logger = get_logger(__name__)


class HyruleAgent:

    def __init__(self):
        self.llm = ChatDeepSeek(
            model=settings.DEEPSEEK_CHAT,  # os.environ.get("DEEPSEEK_CHAT"),
            api_key=settings.DEEPSEEK_API_KEY,  # os.environ.get("DEEPSEEK_API_KEY"),
        )
        self.prompt = HyrulePrompt().prompt_structure()
        self.chat_memory = ChatMemory()
        self.mcp_client = mcp_client

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
