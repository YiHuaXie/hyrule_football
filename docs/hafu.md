# 竞彩足球半全场玩法 (hafu) 字段定义与玩法说明

## 玩法说明
- `hafu` = Half/Full，即 **半场/全场胜平负玩法**。
- 投注规则：
  - 预测半场结果 + 全场结果，共 9 种组合：
    - H = 主胜, D = 平局, A = 客胜
    - 组合格式：半场 + 全场，如 HH = 半场主胜 + 全场主胜
  - 对应字段：
    - hh / hhf：半场主胜 + 全场主胜赔率及浮动值
    - hd / hdf：半场主胜 + 全场平局赔率及浮动值
    - ha / haf：半场主胜 + 全场客胜赔率及浮动值
    - dh / dhf：半场平局 + 全场主胜赔率及浮动值
    - dd / ddf：半场平局 + 全场平局赔率及浮动值
    - da / daf：半场平局 + 全场客胜赔率及浮动值
    - ah / ahf：半场客胜 + 全场主胜赔率及浮动值
    - ad / adf：半场客胜 + 全场平局赔率及浮动值
    - aa / aaf：半场客胜 + 全场客胜赔率及浮动值
- goalLine / goalLineValue：一般为空，仅让球玩法才有值
- updateDate / updateTime：赔率更新时间
- id：玩法编号或记录 ID

---

## 字段定义

| 字段 | 含义 | 类型 | 备注 |
|------|------|------|------|
| hh   | 半场主胜 + 全场主胜赔率 | string | 示例: "2.25" |
| hhf  | hh 浮动值 | string |  |
| hd   | 半场主胜 + 全场平局赔率 | string | 示例: "17.00" |
| hdf  | hd 浮动值 | string |  |
| ha   | 半场主胜 + 全场客胜赔率 | string | 示例: "40.00" |
| haf  | ha 浮动值 | string |  |
| dh   | 半场平局 + 全场主胜赔率 | string | 示例: "3.90" |
| dhf  | dh 浮动值 | string |  |
| dd   | 半场平局 + 全场平局赔率 | string | 示例: "6.40" |
| ddf  | dd 浮动值 | string |  |
| da   | 半场平局 + 全场客胜赔率 | string | 示例: "12.00" |
| daf  | da 浮动值 | string |  |
| ah   | 半场客胜 + 全场主胜赔率 | string | 示例: "20.00" |
| ahf  | ah 浮动值 | string |  |
| ad   | 半场客胜 + 全场平局赔率 | string | 示例: "17.00" |
| adf  | ad 浮动值 | string |  |
| aa   | 半场客胜 + 全场客胜赔率 | string | 示例: "8.25" |
| aaf  | aa 浮动值 | string |  |
| goalLine | 让球盘口 | string | 一般为空 |
| goalLineValue | 让球数值 | string | 一般为空 |
| id    | 玩法 ID | string | 示例: 0 |
| updateDate | 更新日期 | string | 示例: "2025-11-11" |
| updateTime | 更新时间 | string | 示例: "19:18:05" |
