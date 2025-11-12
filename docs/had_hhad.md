# 竞彩足球胜平负 (had)/让球胜平负玩法 (hhad) 字段定义与玩法说明

## 玩法说明
- `had` 是 "Home/Away/Draw" 的缩写，即 **胜平负玩法**。
- `hhad` 是 "Handicap Home/Away/Draw"，即 **让球胜平负玩法**。

- 玩法规则：
  - **主胜（h）**：投注主队获胜；
  - **平局（d）**：投注比赛打平；
  - **客胜（a）**：投注客队获胜。
  - goalLine 表示让球数，例如 "+1" 表示主队让 1 球
  - 主胜/平/客胜赔率按让球后结果计算
  - hf/df/af 标记对应赔率是否变化
  - updateDate / updateTime 表示赔率更新时间

- 注意事项：
  - 赔率会随市场浮动，每个赔率字段有对应的浮动标志（hf、df、af）；
  - `goalLine` 和 `goalLineValue` 一般为空，只有让球玩法才有值；

## 字段定义

| 字段 | 含义 | 类型 | 备注 |
|------|------|------|------|
| h    | 主胜赔率 | string | 赔率浮动值，示例: "2.53" |
| d    | 平局赔率 | string | 赔率浮动值，示例: "3.15" |
| a    | 客胜赔率 | string | 赔率浮动值，示例: "2.40" |
| hf   | 主胜浮动标志 | string |  |
| df   | 平局浮动标志 | string |  |
| af   | 客胜浮动标志 | string |  |
| goalLine | 让球盘口 | string | 一般为空，让球玩法才有值 |
| goalLineValue | 让球数值 | string | 一般为空 |
| updateDate | 更新日期 | string | 示例: "2025-11-11" |
| updateTime | 更新时间 | string | 示例: "21:17:55" |
