# LeagueSeasonTeam 最终设计文档

## 📋 **设计理念**

`LeagueSeasonTeam` 是一个**纯关联表**，只存储联赛、赛季、球队的关联关系，不存储冗余数据。

---

## 🗂️ **表结构**

| 字段名 | 类型 | 说明 | 必填 |
|--------|------|------|------|
| `id` | Integer | 主键ID（自增） | ✅ |
| `league_id` | Integer | 联赛ID（外键 → league.id） | ✅ |
| `season` | String(20) | 赛季（如：2024-2025） | ✅ |
| `team_id` | Integer | 球队ID（外键 → team.id） | ✅ |
| `created_at` | DateTime | 创建时间（UTC） | ✅ |
| `updated_at` | DateTime | 更新时间（UTC） | ✅ |

---

## 🔑 **索引和约束**

### **1. 复合索引**
```python
Index("idx_league_season", "league_id", "season")
Index("idx_team_season", "team_id", "season")
```

**用途：**
- `idx_league_season` - 查询某联赛某赛季的所有球队
- `idx_team_season` - 查询某球队某赛季参加的联赛

### **2. 唯一约束**
```python
UniqueConstraint("league_id", "season", "team_id", name="uq_league_season_team")
```

**用途：** 确保同一联赛同一赛季中，同一球队只能出现一次

---

## 📊 **与之前设计的对比**

### **❌ 之前的设计（冗余字段过多）**

```python
class LeagueSeasonTeam(Base):
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, nullable=False)
    season = Column(String(20), nullable=False)
    team_id = Column(Integer, nullable=False)
    
    # ❌ 冗余字段（应该从 team 表查询）
    oh_team_id = Column(String(64))
    dqd_team_id = Column(String(64))
    team_name = Column(String(100))
    team_short_name = Column(String(50))
    
    # ❌ 业务字段（应该放在单独的表）
    rank = Column(Integer)
    is_active = Column(Integer)
```

**问题：**
- ❌ 冗余存储球队信息（team 表已有）
- ❌ 球队改名时需要同步更新
- ❌ 数据不一致风险
- ❌ 表结构臃肿

---

### **✅ 现在的设计（简洁纯粹）**

```python
class LeagueSeasonTeam(Base):
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, nullable=False)
    season = Column(String(20), nullable=False)
    team_id = Column(Integer, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**优点：**
- ✅ 只存储关联关系
- ✅ 球队信息从 team 表 JOIN 查询
- ✅ 数据一致性高
- ✅ 表结构简洁

---

## 💡 **使用示例**

### **示例1: 添加球队到联赛赛季**

```python
from hyrule_football.models.league_season_team import LeagueSeasonTeam

# 添加曼联到 2024-2025 赛季英超
lst = LeagueSeasonTeam(
    league_id=1,        # 英超
    season="2024-2025",
    team_id=101         # 曼联
)
session.add(lst)
session.commit()
```

### **示例2: 查询某联赛某赛季的所有球队**

```python
from hyrule_football.models.league_season_team import LeagueSeasonTeam
from hyrule_football.models.team import Team

# 查询 2024-2025 赛季英超的所有球队
results = session.query(LeagueSeasonTeam, Team).join(
    Team, LeagueSeasonTeam.team_id == Team.id
).filter(
    LeagueSeasonTeam.league_id == 1,
    LeagueSeasonTeam.season == "2024-2025"
).all()

for lst, team in results:
    print(f"{team.name} - 欧核ID: {team.oh_id}, 懂球帝ID: {team.dqd_id}")
```

### **示例3: 查询某球队参加过的所有联赛赛季**

```python
from hyrule_football.models.league_season_team import LeagueSeasonTeam
from hyrule_football.models.league import League

# 查询曼联参加过的所有联赛赛季
results = session.query(LeagueSeasonTeam, League).join(
    League, LeagueSeasonTeam.league_id == League.id
).filter(
    LeagueSeasonTeam.team_id == 101
).order_by(
    LeagueSeasonTeam.season.desc()
).all()

for lst, league in results:
    print(f"{lst.season} - {league.name}")
```

### **示例4: 批量导入球队**

```python
# 批量添加 2024-2025 赛季英超的 20 支球队
teams_data = [
    {"league_id": 1, "season": "2024-2025", "team_id": 101},  # 曼联
    {"league_id": 1, "season": "2024-2025", "team_id": 102},  # 利物浦
    {"league_id": 1, "season": "2024-2025", "team_id": 103},  # 曼城
    # ... 更多球队
]

for data in teams_data:
    lst = LeagueSeasonTeam(**data)
    session.add(lst)

session.commit()
```

---

## 🎯 **设计原则**

### **1. 单一职责**
- 只存储联赛-赛季-球队的关联关系
- 不存储球队的详细信息（从 team 表查询）
- 不存储联赛的详细信息（从 league 表查询）

### **2. 数据一致性**
- 球队信息只在 team 表维护
- 联赛信息只在 league 表维护
- 避免数据冗余和不一致

### **3. 查询性能**
- 通过索引优化常用查询
- 使用 JOIN 查询详细信息

---

## 📊 **数据示例**

| id | league_id | season | team_id | created_at |
|----|-----------|--------|---------|------------|
| 1 | 1 | 2024-2025 | 101 | 2024-12-10 12:00:00 |
| 2 | 1 | 2024-2025 | 102 | 2024-12-10 12:00:01 |
| 3 | 1 | 2023-2024 | 101 | 2024-12-10 12:00:02 |
| 4 | 2 | 2024-2025 | 101 | 2024-12-10 12:00:03 |

**说明：**
- 记录1: 曼联参加 2024-2025 赛季英超
- 记录2: 利物浦参加 2024-2025 赛季英超
- 记录3: 曼联参加 2023-2024 赛季英超
- 记录4: 曼联参加 2024-2025 赛季西甲

---

## ✅ **总结**

✅ **简洁设计**
- 只有 6 个字段
- 只存储关联关系

✅ **数据一致性**
- 无冗余字段
- 球队信息从 team 表查询

✅ **性能优化**
- 合理的索引设计
- 支持高效 JOIN 查询

✅ **扩展性好**
- 如需添加排名等信息，可创建单独的表
- 保持关联表的纯粹性

**这是一个标准的关联表设计！** 🚀

