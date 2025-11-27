from langchain_community.chat_message_histories import RedisChatMessageHistory

# from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek
from hyrule_football.utils import get_logger
import os

logger = get_logger(__name__)


class ChatMemory:
    """会话记忆系统"""

    def __init__(
        self,
        memory_ttl: int = 300,
        summarize_threshold: int = 40,
    ):
        self.summarize_threshold = summarize_threshold
        self.memory_ttl = memory_ttl
        self.llm = ChatDeepSeek(
            model=os.environ.get("DEEPSEEK_CHAT"),
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
        )

        self.redis_url = os.getenv("REDIS_DEFAULT_URL")

    # -------------------------------------------------------------------------
    #  自动摘要逻辑
    # -------------------------------------------------------------------------
    def _summarize_messages(self, raw_messages: str):
        """把超过长度的完整对话文本进行摘要。"""
        system_prompt = (
            "你是一名会话摘要助手。请阅读下面的多轮对话，"
            "用第一人称“我”进行简洁总结，并提取重要的长期信息。\n"
            "输出格式：\n总结摘要 | 过去对话关键信息"
        )
        prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("user", "{input}")])
        chain = prompt | self.llm
        return chain.invoke({"input": raw_messages})

    # -------------------------------------------------------------------------
    #  加载长期记忆（Redis）并自动摘要
    # -------------------------------------------------------------------------
    def get_history(self, session_id: str) -> RedisChatMessageHistory:
        """加载 Redis 中的历史消息，如果超过 summarize_threshold 条对话，则自动摘要"""

        history = RedisChatMessageHistory(
            url=self.redis_url,
            session_id=session_id,
            # 节约token，设置一个记忆时间，超过记忆时间后若Redis没有写入新数据，意味着会话结束了
            ttl=self.memory_ttl,
        )

        if len(history.messages) >= self.summarize_threshold:
            logger.info("⚠️ 自动摘要 Redis 历史中...")

            full_text = "\n".join(f"{type(m).__name__}: {m.content}" for m in history.messages)
            summary_msg = self._summarize_messages(full_text)

            history.clear()
            history.add_message(summary_msg)

        return history
