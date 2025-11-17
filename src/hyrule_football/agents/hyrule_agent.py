# from langchain.agents import AgentExecutor, create_tool_calling_agent, create_structured_chat_agent
# from langchain_deepseek import ChatDeepSeek
# from langchain_core.runnables import ConfigurableField

from dotenv import load_dotenv
from hyrule_football.store import OddsStore
from hyrule_football.third.ouhe.ouhe_odds import OHAsiaOdds
from hyrule_football.core.odds_pattern import generate_euro_odds_pattern
from hyrule_football.core.odds_engine import OddsEngine
from hyrule_football.utils import water_level_standadrd_str, parse_asia_handicap_smart
from hyrule_football.models import AsiaOdds
from hyrule_football.services import get_match_for_name, get_hot_match_list, request_hot_match_list

load_dotenv()


class HyruleAgent:

    def __init__(self):
        pass

    def run_agent(self, message_text: str, user_id: str) -> dict:
        if message_text == "热门":
            matches = request_hot_match_list()
            match_list = [m.match_description for m in matches]
            return {"output": "\n".join(match_list)}
        if message_text.startswith("赔率&"):
            parts = message_text[3:].strip().split("&")
            print(parts)
            asia_odds = AsiaOdds(
                goal_line=parse_asia_handicap_smart(parts[1]),
                water_level=water_level_standadrd_str(parts[2]),
                return_rate=95.0,
            )

            print(asia_odds.model_dump())

            odds_engine = OddsEngine(parts[0])
            standard_odds_list = odds_engine.filter_standard_odds_from_asia(asia_odds)
            odds_range = OddsEngine.euro_odds_range(standard_odds_list)
            return {"output": f"{odds_range.range_description}"}
        if message_text.startswith("比赛&"):
            return {"output": "赛事查询功能正在开发中"}

        return {"output": "不知道你在说什么"}
