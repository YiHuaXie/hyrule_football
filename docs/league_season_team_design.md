# LeagueSeasonTeam 表设计文档

## 📋 **表说明**

`LeagueSeasonTeam` 是一个**联赛-赛季-球队**的关联表，用于记录：
- 某个赛季中，某个联赛包含哪些球队
- 球队在该赛季的相关信息（排名、平台ID等）

---

## 🗂️ **表结构**

| 字段名 | 类型 | 说明 | 索引 | 必填 |
|--------|------|------|------|------|
| `id` | Integer | 主键ID（自增） | PK | ✅ |
| `league_id` | Integer | 联赛ID | ✅ | ✅ |
| `season` | String(20) | 赛季（如：2024-2025） | ✅ | ✅ |
| `team_id` | Integer | 球队ID | ✅ | ✅ |
| `oh_team_id` | String(64) | 欧核平台球队ID | ✅ | ❌ |
| `dqd_team_id` | String(64) | 懂球帝平台球队ID | ✅ | ❌ |
| `team_name` | String(100) | 球队名称（冗余） | ❌ | ✅ |
| `team_short_name` | String(50) | 球队简称 | ❌ | ❌ |
| `rank` | Integer | 赛季排名 | ❌ | ❌ |
| `is_active` | Integer | 是否激活（1=激活，0=禁用） | ❌ | ✅ |
| `created_at` | DateTime | 创建时间 | ❌ | ✅ |
| `updated_at` | DateTime | 更新时间 | ❌ | ✅ |

---

## 🔑 **索引设计**

### **1. 单列索引**
- `league_id` - 按联赛查询
- `season` - 按赛季查询
- `team_id` - 按球队查询
- `oh_team_id` - 按欧核球队ID查询
- `dqd_team_id` - 按懂球帝球队ID查询

### **2. 复合索引**
- `idx_league_season` - (`league_id`, `season`) - 查询某联赛的某赛季
- `idx_league_season_team` - (`league_id`, `season`, `team_id`) - **唯一索引**，确保同一联赛同一赛季中球队不重复

---

## 💡 **使用场景**

### **场景1: 查询某联赛某赛季的所有球队**

```python
from sqlalchemy.orm import Session
from hyrule_football.models.league_season_team import LeagueSeasonTeam

def get_teams_by_league_season(session: Session, league_id: int, season: str):
    """查询某联赛某赛季的所有球队"""
    return session.query(LeagueSeasonTeam).filter(
        LeagueSeasonTeam.league_id == league_id,
        LeagueSeasonTeam.season == season,
        LeagueSeasonTeam.is_active == 1
    ).order_by(LeagueSeasonTeam.rank).all()

# 使用示例
teams = get_teams_by_league_season(session, league_id=1, season="2024-2025")
for team in teams:
    print(f"{team.rank}. {team.team_name}")
```

### **场景2: 添加球队到联赛赛季**

```python
def add_team_to_league_season(
    session: Session,
    league_id: int,
    season: str,
    team_id: int,
    team_name: str,
    oh_team_id: str = None,
    dqd_team_id: str = None,
    rank: int = None
):
    """添加球队到联赛赛季"""
    team = LeagueSeasonTeam(
        league_id=league_id,
        season=season,
        team_id=team_id,
        team_name=team_name,
        oh_team_id=oh_team_id,
        dqd_team_id=dqd_team_id,
        rank=rank
    )
    session.add(team)
    session.commit()
    return team

# 使用示例
add_team_to_league_season(
    session,
    league_id=1,  # 英超
    season="2024-2025",
    team_id=101,
    team_name="曼彻斯特联",
    oh_team_id="oh_team_123",
    dqd_team_id="dqd_team_456",
    rank=5
)
```

### **场景3: 批量导入球队**

```python
def batch_import_teams(session: Session, league_id: int, season: str, teams_data: list):
    """批量导入球队到联赛赛季"""
    teams = []
    for data in teams_data:
        team = LeagueSeasonTeam(
            league_id=league_id,
            season=season,
            team_id=data['team_id'],
            team_name=data['team_name'],
            oh_team_id=data.get('oh_team_id'),
            dqd_team_id=data.get('dqd_team_id'),
            rank=data.get('rank')
        )
        teams.append(team)
    
    session.bulk_save_objects(teams)
    session.commit()

# 使用示例
teams_data = [
    {'team_id': 101, 'team_name': '曼联', 'rank': 1},
    {'team_id': 102, 'team_name': '利物浦', 'rank': 2},
    {'team_id': 103, 'team_name': '曼城', 'rank': 3},
]
batch_import_teams(session, league_id=1, season="2024-2025", teams_data=teams_data)
```

### **场景4: 查询球队参加过的所有联赛赛季**

```python
def get_team_history(session: Session, team_id: int):
    """查询球队参加过的所有联赛赛季"""
    return session.query(LeagueSeasonTeam).filter(
        LeagueSeasonTeam.team_id == team_id,
        LeagueSeasonTeam.is_active == 1
    ).order_by(LeagueSeasonTeam.season.desc()).all()

# 使用示例
history = get_team_history(session, team_id=101)
for record in history:
    print(f"{record.season} - 联赛ID: {record.league_id}, 排名: {record.rank}")
```

---

## 🎯 **设计要点**

### **1. 唯一约束**
- (`league_id`, `season`, `team_id`) 组合唯一
- 确保同一联赛同一赛季中，同一球队只能出现一次

### **2. 冗余字段**
- `team_name` 和 `team_short_name` 是冗余字段
- 优点：查询时无需 JOIN 球队表，提升性能
- 缺点：球队改名时需要同步更新

### **3. 平台ID字段**
- `oh_team_id` 和 `dqd_team_id` 用于关联不同平台的球队
- 可以为空，因为可能某些平台没有该球队数据

### **4. 软删除**
- 使用 `is_active` 字段实现软删除
- 不直接删除记录，方便数据恢复和历史查询

---

## 📊 **数据示例**

| id | league_id | season | team_id | team_name | rank | oh_team_id | dqd_team_id |
|----|-----------|--------|---------|-----------|------|------------|-------------|
| 1 | 1 | 2024-2025 | 101 | 曼彻斯特联 | 5 | oh_123 | dqd_456 |
| 2 | 1 | 2024-2025 | 102 | 利物浦 | 1 | oh_124 | dqd_457 |
| 3 | 1 | 2023-2024 | 101 | 曼彻斯特联 | 3 | oh_123 | dqd_456 |

---

## ✅ **总结**

✅ **核心功能**
- 记录联赛-赛季-球队的关联关系
- 支持多平台球队ID映射
- 支持球队排名记录

✅ **性能优化**
- 合理的索引设计
- 冗余字段减少JOIN

✅ **数据完整性**
- 唯一约束防止重复
- 软删除保留历史数据

