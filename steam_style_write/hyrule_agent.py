from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain_core.runnables import RunnableWithMessageHistory
from hyrule_football.config import settings
from hyrule_football.utils import get_logger
from hyrule_football.agents.prompts.hyrule_prompt import HyrulePrompt
from hyrule_football.agents.memory.chat_memory import ChatMemory
from hyrule_football.mcp.mcp_client import mcp_client

logger = get_logger(__name__)


class HyruleAgent:

    def __init__(self):
        self.llm = ChatDeepSeek(
            model=settings.DEEPSEEK_CHAT,
            api_key=settings.DEEPSEEK_API_KEY,
            streaming=True,  # 启用流式输出
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

    async def run_agent_stream(self, message_text: str, user_id: str):
        """流式运行 Agent（返回异步生成器）"""
        try:
            if not hasattr(self, "agent"):
                await self._create_agent()

            history = self.agent_with_memory.get_session_history(user_id)
            history.add_user_message(message_text)

            buffer = ""  # 缓冲区，累积字符
            buffer_size = 10  # 每累积 10 个字符才输出一次

            # 使用 astream_events 获取流式输出
            async for event in self.agent_with_memory.astream_events(
                {},
                config={"configurable": {"session_id": user_id}},
                version="v2",
            ):
                kind = event["event"]

                # 捕获 LLM 的流式输出
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        buffer += content

                        # 当缓冲区达到指定大小时，输出
                        if len(buffer) >= buffer_size:
                            yield buffer
                            buffer = ""

                # 捕获工具调用信息（可选）
                elif kind == "on_tool_start":
                    # 先输出缓冲区剩余内容
                    if buffer:
                        yield buffer
                        buffer = ""

                    tool_name = event["name"]
                    logger.info(f"🔧 调用工具: {tool_name}")
                    yield f"\n\n🔧 正在调用工具: {tool_name}...\n\n"

                elif kind == "on_tool_end":
                    logger.info(f"✅ 工具调用完成")

            # 输出缓冲区剩余内容
            if buffer:
                yield buffer

        except Exception as e:
            logger.exception(f"Hyrule Agent Stream Error: {e}")
            yield "抱歉，处理消息时出现错误。"
