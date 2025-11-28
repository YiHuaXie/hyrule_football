from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain_core.runnables import RunnableWithMessageHistory
from hyrule_football.config import settings
from hyrule_football.utils import get_logger
from hyrule_football.prompts.hyrule_prompt import HyrulePrompt
from hyrule_football.memory.chat_memory import ChatMemory
from hyrule_football.tools import (
    get_match_list,
    get_match_for_team,
    get_match_for_matchup,
    get_odds_info_for_match,
    plan_match_odds_query,
)

logger = get_logger(__name__)


class HyruleAgent:

    def __init__(self):
        self.llm = ChatDeepSeek(
            model=settings.DEEPSEEK_CHAT,  # os.environ.get("DEEPSEEK_CHAT"),
            api_key=settings.DEEPSEEK_API_KEY,  # os.environ.get("DEEPSEEK_API_KEY"),
        )

        self.tools = [
            get_match_list,
            get_match_for_team,
            get_match_for_matchup,
            get_odds_info_for_match,
            plan_match_odds_query,
        ]

        self.prompt = HyrulePrompt().prompt_structure()

        # # 创建 Agent（单智能体）
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.prompt,
            debug=True,
        )

        self.chat_memory = ChatMemory()

        self.agent_with_memory = RunnableWithMessageHistory(
            self.agent,
            get_session_history=self.chat_memory.get_history,
            input_messages_key="messages",
            history_messages_key="messages",
        )

    def run_agent(self, message_text: str, user_id: str) -> str:
        try:
            history = self.agent_with_memory.get_session_history(user_id)
            history.add_user_message(message_text)

            result = self.agent_with_memory.invoke(
                {},
                config={"configurable": {"session_id": user_id}},
            )
            messages = result["messages"]
            return messages[-1].content
        except Exception as e:
            logger.error(f"Hyrule Agent Error: {e}")
            return "暂时不知道你在说什么"
