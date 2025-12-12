from typing import Tuple, Literal
from rapidfuzz import fuzz


class TeamMatcher:

    def __init__(self, high_threshold: int = 85, medium_threshold: int = 75):
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def is_match(
        self,
        home: str,
        away: str,
        team_a: str,
        team_b: str,
    ) -> Tuple[bool, Literal["team_a", "team_b", ""]]:
        """判断两场比赛的球队是否匹配，并识别哪个是主场"""
        # 快速路径：完全匹配判断（避免相似度计算）
        if team_a == home and team_b == away:
            return True, "team_a"
        if team_b == home and team_a == away:
            return True, "team_b"

        # 慢速路径：相似度匹配
        # 情况1: team_a 是主场，team_b 是客场
        score_normal = self._calculate_match_score(home, away, team_a, team_b)

        # 情况2: team_b 是主场，team_a 是客场
        score_reversed = self._calculate_match_score(home, away, team_b, team_a)

        # 判断哪种情况分数更高
        if score_normal >= score_reversed:
            # team_a 是主场
            if score_normal >= self.high_threshold:
                return True, "team_a"
            elif score_normal >= self.medium_threshold:
                # 使用 combined 方法辅助验证
                score_comb = self._calculate_combined_score_for_match(home, away, team_a, team_b)
                if score_comb >= self.high_threshold:
                    return True, "team_a"
        else:
            # team_b 是主场
            if score_reversed >= self.high_threshold:
                return True, "team_b"
            elif score_reversed >= self.medium_threshold:
                # 使用 combined 方法辅助验证
                score_comb = self._calculate_combined_score_for_match(home, away, team_b, team_a)
                if score_comb >= self.high_threshold:
                    return True, "team_b"

        # 不匹配
        return False, ""

    def _calculate_team_similarity(self, team1: str, team2: str) -> float:
        """计算两个球队名称的相似度"""
        if not team1 or not team2:
            return 0.0

        ratio = fuzz.ratio(team1, team2)
        partial = fuzz.partial_ratio(team1, team2)
        token_sort = fuzz.token_sort_ratio(team1, team2)

        return max(ratio, partial, token_sort)

    def _calculate_match_score(
        self,
        home: str,
        away: str,
        team_home: str,
        team_away: str,
    ) -> float:
        """
        计算比赛匹配分数（假设 team_home 是主场，team_away 是客场）
        """
        home_sim = self._calculate_team_similarity(home, team_home)
        away_sim = self._calculate_team_similarity(away, team_away)
        return (home_sim + away_sim) / 2

    def _calculate_combined_score_for_match(
        self,
        home: str,
        away: str,
        team_home: str,
        team_away: str,
    ) -> float:
        """
        使用合并字符串方法计算匹配分数
        """
        match1 = f"{home} vs {away}"
        match2 = f"{team_home} vs {team_away}"

        ratio = fuzz.ratio(match1, match2)
        partial = fuzz.partial_ratio(match1, match2)
        token_sort = fuzz.token_sort_ratio(match1, match2)

        return max(ratio, partial, token_sort)
