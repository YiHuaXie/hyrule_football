"""
竞彩足球胜平负 (HAD) 模型

HAD = Home/Away/Draw (胜平负玩法)

玩法规则：
- 主胜（h）：投注主队获胜
- 平局（d）：投注比赛打平
- 客胜（a）：投注客队获胜
"""

from datetime import date, time
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator, ConfigDict


class HADModel(BaseModel):
    """
    胜平负玩法 (HAD) 数据模型
    
    预测比赛结果：
    - h: 主胜 (Home win)
    - d: 平局 (Draw)
    - a: 客胜 (Away win)
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,  # 允许使用字段名或别名
    )
    
    # 赔率字段
    h: str = Field(
        ...,
        description="主胜赔率",
        examples=["2.53", "1.85"]
    )
    d: str = Field(
        ...,
        description="平局赔率",
        examples=["3.15", "3.40"]
    )
    a: str = Field(
        ...,
        description="客胜赔率",
        examples=["2.40", "4.20"]
    )
    
    # 赔率浮动标志
    hf: Literal[0, 1] = Field(
        default=0,
        description="主胜赔率浮动标志，0=未变化，1=已变化"
    )
    df: Literal[0, 1] = Field(
        default=0,
        description="平局赔率浮动标志，0=未变化，1=已变化"
    )
    af: Literal[0, 1] = Field(
        default=0,
        description="客胜赔率浮动标志，0=未变化，1=已变化"
    )
    
    # 让球相关字段（HAD 玩法中一般为空）
    goal_line: Optional[str] = Field(
        default=None,
        alias="goalLine",
        description="让球盘口，HAD 玩法中一般为空"
    )
    goal_line_value: Optional[str] = Field(
        default=None,
        alias="goalLineValue",
        description="让球数值，HAD 玩法中一般为空"
    )
    
    # 更新时间
    update_date: str = Field(
        ...,
        alias="updateDate",
        description="赔率更新日期",
        examples=["2025-11-11"]
    )
    update_time: str = Field(
        ...,
        alias="updateTime",
        description="赔率更新时间",
        examples=["21:17:55"]
    )
    
    @field_validator("h", "d", "a")
    @classmethod
    def validate_odds(cls, v: str) -> str:
        """验证赔率格式，确保可以转换为有效的数字"""
        try:
            odds_value = Decimal(v)
            if odds_value <= 0:
                raise ValueError("赔率必须大于 0")
            return v
        except Exception as e:
            raise ValueError(f"无效的赔率格式: {v}") from e
    
    @field_validator("update_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """验证日期格式 YYYY-MM-DD"""
        try:
            # 尝试解析日期
            date.fromisoformat(v)
            return v
        except ValueError as e:
            raise ValueError(f"无效的日期格式，应为 YYYY-MM-DD: {v}") from e
    
    @field_validator("update_time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        """验证时间格式 HH:MM:SS"""
        try:
            # 尝试解析时间
            time.fromisoformat(v)
            return v
        except ValueError as e:
            raise ValueError(f"无效的时间格式，应为 HH:MM:SS: {v}") from e
    
    def get_odds_as_decimal(self) -> dict[str, Decimal]:
        """获取赔率的 Decimal 格式"""
        return {
            "h": Decimal(self.h),
            "d": Decimal(self.d),
            "a": Decimal(self.a),
        }
    
    def get_changed_odds(self) -> list[str]:
        """获取发生变化的赔率类型"""
        changed = []
        if self.hf == 1:
            changed.append("h")
        if self.df == 1:
            changed.append("d")
        if self.af == 1:
            changed.append("a")
        return changed
    
    def has_odds_changed(self) -> bool:
        """判断是否有赔率发生变化"""
        return self.hf == 1 or self.df == 1 or self.af == 1
    
    def get_lowest_odds(self) -> tuple[str, Decimal]:
        """
        获取最低赔率及其类型
        最低赔率通常表示最可能的结果
        """
        odds = self.get_odds_as_decimal()
        min_type = min(odds, key=odds.get)
        return min_type, odds[min_type]
    
    def get_highest_odds(self) -> tuple[str, Decimal]:
        """
        获取最高赔率及其类型
        最高赔率通常表示最不可能的结果
        """
        odds = self.get_odds_as_decimal()
        max_type = max(odds, key=odds.get)
        return max_type, odds[max_type]
    
    def calculate_probability(self) -> dict[str, float]:
        """
        根据赔率计算隐含概率
        概率 = 1 / 赔率
        
        注意：实际概率总和会大于 1（包含博彩公司的利润率）
        """
        odds = self.get_odds_as_decimal()
        return {
            "h": float(1 / odds["h"]),
            "d": float(1 / odds["d"]),
            "a": float(1 / odds["a"]),
        }
    
    def get_bookmaker_margin(self) -> float:
        """
        计算博彩公司的利润率（overround）
        利润率 = (1/h + 1/d + 1/a) - 1
        
        返回值示例：0.05 表示 5% 的利润率
        """
        probs = self.calculate_probability()
        total_prob = sum(probs.values())
        return total_prob - 1.0
    
    def get_fair_odds(self) -> dict[str, Decimal]:
        """
        计算去除利润率后的公平赔率
        公平赔率 = 原赔率 * (1 + 利润率)
        """
        margin = self.get_bookmaker_margin()
        odds = self.get_odds_as_decimal()
        return {
            key: value * Decimal(1 + margin)
            for key, value in odds.items()
        }
    
    def predict_most_likely_outcome(self) -> str:
        """
        预测最可能的结果（基于最低赔率）
        
        返回：'h' (主胜), 'd' (平局), 或 'a' (客胜)
        """
        outcome, _ = self.get_lowest_odds()
        return outcome
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "h": self.h,
            "d": self.d,
            "a": self.a,
            "hf": self.hf,
            "df": self.df,
            "af": self.af,
            "goalLine": self.goal_line,
            "goalLineValue": self.goal_line_value,
            "updateDate": self.update_date,
            "updateTime": self.update_time,
        }

