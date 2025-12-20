"""
MCP 智能路由器
根据用户问题选择需要连接的 MCP Server
"""

from typing import List, Set
import re


class MCPRouter:
    """MCP 智能路由器"""

    # MCP 关键词映射
    KEYWORDS_MAP = {
        "company": [
            "博彩公司", "公司", "庄家", "bookmaker",
            "bet365", "威廉希尔", "澳门", "立博",
        ],
        "match": [
            "比赛", "对阵", "赛程", "赛果", "比分",
            "球队", "主队", "客队", "vs",
            "match", "game", "fixture",
        ],
        "odds": [
            "赔率", "盘口", "水位", "让球", "大小球",
            "欧赔", "亚盘", "初盘", "即时盘",
            "odds", "handicap", "over/under",
        ],
        "league": [
            "联赛", "赛季", "积分榜", "排名",
            "英超", "西甲", "德甲", "意甲", "法甲",
            "league", "season", "standings",
        ],
        "team": [
            "球队", "阵容", "球员", "教练",
            "曼联", "巴萨", "皇马", "拜仁",
            "team", "squad", "player",
        ],
    }

    # 默认加载的 MCP（核心功能）
    DEFAULT_MCPS = ["match", "odds"]

    @classmethod
    def route(cls, user_question: str) -> List[str]:
        """
        根据用户问题选择需要的 MCP
        
        Args:
            user_question: 用户问题
            
        Returns:
            需要连接的 MCP 列表，例如 ["match", "odds"]
        """
        needed_mcps: Set[str] = set()
        question_lower = user_question.lower()

        # 遍历关键词映射
        for mcp_name, keywords in cls.KEYWORDS_MAP.items():
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    needed_mcps.add(mcp_name)
                    break

        # 如果没有匹配，返回默认 MCP
        if not needed_mcps:
            return cls.DEFAULT_MCPS.copy()

        return list(needed_mcps)

    @classmethod
    def route_with_reason(cls, user_question: str) -> dict:
        """
        根据用户问题选择需要的 MCP，并返回原因
        
        Returns:
            {
                "mcps": ["match", "odds"],
                "reason": "检测到关键词：比赛、赔率",
                "matched_keywords": {"match": ["比赛"], "odds": ["赔率"]}
            }
        """
        needed_mcps: Set[str] = set()
        matched_keywords = {}
        question_lower = user_question.lower()

        # 遍历关键词映射
        for mcp_name, keywords in cls.KEYWORDS_MAP.items():
            matched = []
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    matched.append(keyword)
            
            if matched:
                needed_mcps.add(mcp_name)
                matched_keywords[mcp_name] = matched

        # 如果没有匹配，返回默认 MCP
        if not needed_mcps:
            return {
                "mcps": cls.DEFAULT_MCPS.copy(),
                "reason": "未检测到特定关键词，使用默认 MCP",
                "matched_keywords": {},
            }

        return {
            "mcps": list(needed_mcps),
            "reason": f"检测到关键词：{', '.join(matched_keywords.keys())}",
            "matched_keywords": matched_keywords,
        }

    @classmethod
    def add_keyword(cls, mcp_name: str, keyword: str):
        """动态添加关键词"""
        if mcp_name not in cls.KEYWORDS_MAP:
            cls.KEYWORDS_MAP[mcp_name] = []
        cls.KEYWORDS_MAP[mcp_name].append(keyword)

    @classmethod
    def set_default_mcps(cls, mcps: List[str]):
        """设置默认 MCP"""
        cls.DEFAULT_MCPS = mcps.copy()


# 使用示例
if __name__ == "__main__":
    # 测试路由
    test_questions = [
        "查询曼联今天的比赛",
        "bet365 的赔率是多少",
        "英超积分榜",
        "曼联的阵容",
        "今天有什么比赛，赔率如何",
        "随便问个问题",
    ]

    for question in test_questions:
        result = MCPRouter.route_with_reason(question)
        print(f"\n问题: {question}")
        print(f"需要的 MCP: {result['mcps']}")
        print(f"原因: {result['reason']}")
        print(f"匹配的关键词: {result['matched_keywords']}")

