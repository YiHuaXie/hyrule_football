"""
竞彩足球让球胜平负 (HHAD) 模型

HHAD = Handicap Home/Away/Draw (让球胜平负玩法)

玩法规则：
- 主胜（h）：投注主队获胜（按让球后结果计算）
- 平局（d）：投注比赛打平（按让球后结果计算）
- 客胜（a）：投注客队获胜（按让球后结果计算）
- goalLine 表示让球数，例如 "+1" 表示主队让 1 球
"""

from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from .had_model import HADModel


class HHADModel(HADModel):
    """
    让球胜平负玩法 (HHAD) 数据模型
    
    继承自 HADModel，但让球字段为必填
    赔率按让球后的结果计算
    """
    
    # 重写让球字段为必填
    goal_line: str = Field(
        ...,
        alias="goalLine",
        description="让球盘口，例如 '+1' 表示主队让 1 球，'-1' 表示主队受让 1 球",
        examples=["+1", "-1", "+2", "-2", "0"]
    )
    goal_line_value: str = Field(
        ...,
        alias="goalLineValue",
        description="让球数值（绝对值）",
        examples=["1", "2", "0"]
    )
    
    @field_validator("goal_line")
    @classmethod
    def validate_goal_line(cls, v: str) -> str:
        """验证让球盘口格式"""
        if not v:
            raise ValueError("让球盘口不能为空")
        
        # 检查格式：应该以 +、- 或数字开头
        if not (v.startswith("+") or v.startswith("-") or v.isdigit()):
            raise ValueError(f"无效的让球盘口格式: {v}，应为 '+1', '-1' 或 '0' 等格式")
        
        return v
    
    @field_validator("goal_line_value")
    @classmethod
    def validate_goal_line_value(cls, v: str) -> str:
        """验证让球数值格式"""
        try:
            value = int(v)
            if value < 0:
                raise ValueError("让球数值不能为负数")
            return v
        except ValueError as e:
            raise ValueError(f"无效的让球数值: {v}，应为非负整数") from e
    
    def get_handicap(self) -> int:
        """
        获取让球数（带符号）
        
        返回值：
        - 正数：主队让球（主队需要净胜 N 球才算赢）
        - 负数：主队受让（主队可以输 N 球内仍算赢）
        - 0：无让球
        
        示例：
        - "+1" -> 1 (主队让 1 球)
        - "-1" -> -1 (主队受让 1 球)
        - "0" -> 0 (无让球)
        """
        if self.goal_line.startswith("+"):
            return int(self.goal_line_value)
        elif self.goal_line.startswith("-"):
            return -int(self.goal_line_value)
        else:
            return int(self.goal_line_value)
    
    def is_home_handicap(self) -> bool:
        """判断是否主队让球（主队强）"""
        return self.get_handicap() > 0
    
    def is_away_handicap(self) -> bool:
        """判断是否主队受让（客队强）"""
        return self.get_handicap() < 0
    
    def is_no_handicap(self) -> bool:
        """判断是否无让球"""
        return self.get_handicap() == 0
    
    def get_handicap_description(self) -> str:
        """
        获取让球描述
        
        返回示例：
        - "主队让 1 球"
        - "主队受让 1 球"
        - "无让球"
        """
        handicap = self.get_handicap()
        if handicap > 0:
            return f"主队让 {handicap} 球"
        elif handicap < 0:
            return f"主队受让 {abs(handicap)} 球"
        else:
            return "无让球"
    
    def calculate_adjusted_result(
        self, 
        home_score: int, 
        away_score: int
    ) -> Literal["h", "d", "a"]:
        """
        根据实际比分和让球数计算调整后的结果
        
        参数：
        - home_score: 主队实际进球数
        - away_score: 客队实际进球数
        
        返回：
        - "h": 主胜（让球后）
        - "d": 平局（让球后）
        - "a": 客胜（让球后）
        
        示例：
        - 实际比分 2:1，让球 +1 -> 调整后 1:1 -> "d"
        - 实际比分 2:1，让球 -1 -> 调整后 3:1 -> "h"
        """
        handicap = self.get_handicap()
        adjusted_home_score = home_score - handicap
        
        if adjusted_home_score > away_score:
            return "h"
        elif adjusted_home_score < away_score:
            return "a"
        else:
            return "d"
    
    def get_expected_score_difference(self) -> int:
        """
        获取市场预期的比分差距（基于让球数）
        
        正数表示主队预期领先，负数表示客队预期领先
        """
        return self.get_handicap()
    
    def compare_with_had(self, had_model: HADModel) -> dict[str, dict]:
        """
        与普通胜平负赔率对比分析
        
        参数：
        - had_model: HADModel 实例
        
        返回：赔率对比和分析
        """
        had_odds = had_model.get_odds_as_decimal()
        hhad_odds = self.get_odds_as_decimal()
        
        comparison = {}
        for key in ["h", "d", "a"]:
            diff = hhad_odds[key] - had_odds[key]
            comparison[key] = {
                "had": float(had_odds[key]),
                "hhad": float(hhad_odds[key]),
                "difference": float(diff),
                "percentage_change": float(diff / had_odds[key] * 100),
            }
        
        return comparison
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        base_dict = super().to_dict()
        base_dict.update({
            "handicap": self.get_handicap(),
            "handicap_description": self.get_handicap_description(),
        })
        return base_dict

