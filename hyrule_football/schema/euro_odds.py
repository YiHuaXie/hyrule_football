from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated


class EuroOdds(BaseModel):
    """生成欧指(胜平负)赔率模型"""

    w: Annotated[float, Field(..., description="胜赔率(Win)")]
    d: Annotated[float, Field(..., description="平赔率(Draw)")]
    l: Annotated[float, Field(..., description="负赔率(Lose)")]
    return_rate: Annotated[float, Field(..., description="返还率")]

    @field_validator("w", "d", "l", "return_rate", mode="before")
    def to_float(cls, v):
        return v if isinstance(v, float) else float(v)

    @property
    def opposite_odds(self):
        """生成对立面的欧指"""
        return EuroOdds(w=self.l, d=self.d, l=self.w, return_rate=self.return_rate)

    @property
    def euro_system_no(self) -> int:
        """获取欧指体系编号"""
        # 每个区间宽度：1，offset 0.8 让区间精准对应
        # 起始区间：88.2 对应体系 89
        # 所以 (88.2 + 0.8 → 89), (89.19 + 0.8 → 89),
        # (89.2 + 0.8 → 90), (90.19 + 0.8 → 90),...
        system_no = int(self.return_rate + 0.8)
        return system_no

    @property
    def euro_odds_under_94(self):
        """将当前欧指转换为94体系下的欧指"""

        # 1. 计算原始概率
        original_return_rate = self.euro_system_no / 100.0
        p_w = original_return_rate / self.w
        p_d = original_return_rate / self.d
        p_l = original_return_rate / self.l

        # 2. 概率归一化
        total = p_w + p_d + p_l
        p_w_norm = p_w / total
        p_d_norm = p_d / total
        p_l_norm = p_l / total

        # 3. 根据当前反推新赔率
        new_return_rate = 0.94
        n_w = new_return_rate / p_w_norm
        n_d = new_return_rate / p_d_norm
        n_l = new_return_rate / p_l_norm

        return EuroOdds(
            w=round(n_w, 2),
            d=round(n_d, 2),
            l=round(n_l, 2),
            return_rate=94.0,
        )
