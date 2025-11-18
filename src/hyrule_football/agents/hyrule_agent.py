# from langchain.agents import AgentExecutor, create_tool_calling_agent, create_structured_chat_agent
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent

# from langchain_core.runnables import ConfigurableField

from dotenv import load_dotenv as _load_dotenv
from hyrule_football.utils import get_logger
from hyrule_football.prompts.hyrule_prompt import HyrulePrompt

from hyrule_football.tools import get_match_list


# from hyrule_football.store import OddsStore

# from hyrule_football.third.ouhe.ouhe_odds import OHAsiaOdds
# from hyrule_football.core.odds_pattern import generate_euro_odds_pattern
# from hyrule_football.core.odds_engine import OddsEngine


# from hyrule_football.models import AsiaOdds
import os

_load_dotenv()

logger = get_logger(__name__)


class HyruleAgent:

    def __init__(self):
        self.llm = ChatDeepSeek(
            model=os.environ.get("DEEPSEEK_CHAT"),
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
        )

        self.tools = [
            get_match_list,
        ]
        self.prompt = HyrulePrompt().prompt_structure()
        # 创建 Agent（单智能体）
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.prompt,
            debug=True,
        )

        # self.agent_executor = AgentExecutor(
        #     agent=self.agent,
        #     tools=self.tools,
        #     # memory=self.memory.set_memory(),
        #     verbose=True,
        # )
        # .configurable_fields(
        #     memory=ConfigurableField(
        #         id="agent_memory",
        #         name="Agent Memory",
        #         description="The memory of the agent",
        #     )
        # )

    def run_agent(self, message_text: str, user_id: str) -> str:
        try:
            result = self.agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": message_text,
                        }
                    ]
                },
            )

            messages = result["messages"]
            return messages[-1].content
        except Exception as e:
            logger.error(f"Hyrule Agent Error: {e}")

        return "暂时不知道你在说什么"

    # if message_text == "热门":
    #     matches = request_hot_match_list()
    #     match_list = [m.match_description for m in matches]
    #     return {"output": "\n".join(match_list)}
    # if message_text.startswith("赔率&"):
    #     parts = message_text[3:].strip().split("&")
    #     print(parts)
    #     asia_odds = AsiaOdds(
    #         goal_line=parse_asia_handicap_smart(parts[1]),
    #         water_level=water_level_standadrd_str(parts[2]),
    #         return_rate=95.0,
    #     )

    #     print(asia_odds.model_dump())

    #     odds_engine = OddsEngine(parts[0])
    #     standard_odds_list = odds_engine.filter_standard_odds_from_asia(asia_odds)
    #     odds_range = OddsEngine.euro_odds_range(standard_odds_list)
    #     return {"output": f"{odds_range.range_description}"}
    # if message_text.startswith("比赛&"):
    #     return {"output": "赛事查询功能正在开发中"}

    # return {"output": "不知道你在说什么"}
