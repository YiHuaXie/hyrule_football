# Team 表设计文档

## 📋 **表说明**

`Team` 是球队基础信息表，用于存储所有球队的核心数据。

---

## 🗂️ **表结构**

| 字段名 | 类型 | 说明 | 索引 | 唯一 | 必填 |
|--------|------|------|------|------|------|
| `id` | Integer | 主键ID（自增） | PK | ✅ | ✅ |
| `name` | String(100) | 球队名称 | ✅ | ❌ | ✅ |
| `short_name` | String(50) | 球队简称 | ❌ | ❌ | ❌ |
| `oh_id` | String(64) | 欧核平台球队ID | ✅ | ✅ | ❌ |
| `dqd_id` | String(64) | 懂球帝平台球队ID | ✅ | ✅ | ❌ |
| `is_active` | Integer | 是否激活（1=激活，0=禁用） | ❌ | ❌ | ✅ |
| `created_at` | DateTime | 创建时间 | ❌ | ❌ | ✅ |
| `updated_at` | DateTime | 更新时间 | ❌ | ❌ | ✅ |

---

## 🔑 **索引和约束**

### **1. 主键**
- `id` - 自增主键

### **2. 唯一索引**
- `oh_id` - 欧核球队ID唯一（同一平台不能有重复球队）
- `dqd_id` - 懂球帝球队ID唯一

### **3. 普通索引**
- `name` - 按球队名称查询

---

## 💡 **设计要点**

### **1. 平台ID唯一性**
```python
oh_id = Column(String(64), nullable=True, index=True, unique=True)
dqd_id = Column(String(64), nullable=True, index=True, unique=True)
```

- `oh_id` 和 `dqd_id` 设置为 `unique=True`
- 确保同一平台的球队ID不会重复
- 可以为 `NULL`（某些球队可能只在一个平台有数据）

### **2. 球队名称**
```python
name = Column(String(100), nullable=False, index=True)
short_name = Column(String(50), nullable=True)
```

- `name` - 完整球队名称（如：曼彻斯特联）
- `short_name` - 球队简称（如：曼联）
- 名称可以重复（不同国家可能有同名球队）

### **3. 软删除**
```python
is_active = Column(Integer, default=1)
```

- 使用 `is_active` 实现软删除
- 不直接删除记录，方便数据恢复

---

## 📝 **使用示例**

### **示例1: 创建球队**

```python
from sqlalchemy.orm import Session
from hyrule_football.models.team import Team

def create_team(
    session: Session,
    name: str,
    short_name: str = None,
    oh_id: str = None,
    dqd_id: str = None
) -> Team:
    """创建球队"""
    team = Team(
        name=name,
        short_name=short_name,
        oh_id=oh_id,
        dqd_id=dqd_id
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    return team

# 使用
team = create_team(
    session,
    name="曼彻斯特联",
    short_name="曼联",
    oh_id="oh_team_123",
    dqd_id="dqd_team_456"
)
print(f"创建球队: {team.name}, ID: {team.id}")
```

### **示例2: 按名称查询球队**

```python
def get_team_by_name(session: Session, name: str) -> Team:
    """按名称查询球队"""
    return session.query(Team).filter(
        Team.name == name,
        Team.is_active == 1
    ).first()

# 使用
team = get_team_by_name(session, "曼彻斯特联")
if team:
    print(f"找到球队: {team.name}, 简称: {team.short_name}")
```

### **示例3: 按平台ID查询球队**

```python
def get_team_by_oh_id(session: Session, oh_id: str) -> Team:
    """按欧核ID查询球队"""
    return session.query(Team).filter(
        Team.oh_id == oh_id,
        Team.is_active == 1
    ).first()

def get_team_by_dqd_id(session: Session, dqd_id: str) -> Team:
    """按懂球帝ID查询球队"""
    return session.query(Team).filter(
        Team.dqd_id == dqd_id,
        Team.is_active == 1
    ).first()

# 使用
team = get_team_by_oh_id(session, "oh_team_123")
if team:
    print(f"欧核球队: {team.name}")
```

### **示例4: 更新球队平台ID**

```python
def update_team_platform_id(
    session: Session,
    team_id: int,
    oh_id: str = None,
    dqd_id: str = None
):
    """更新球队平台ID"""
    team = session.query(Team).filter(Team.id == team_id).first()
    if team:
        if oh_id:
            team.oh_id = oh_id
        if dqd_id:
            team.dqd_id = dqd_id
        session.commit()
        return team
    return None

# 使用
update_team_platform_id(session, team_id=1, oh_id="oh_new_123")
```

### **示例5: 批量导入球队**

```python
def batch_import_teams(session: Session, teams_data: list):
    """批量导入球队"""
    teams = []
    for data in teams_data:
        team = Team(
            name=data['name'],
            short_name=data.get('short_name'),
            oh_id=data.get('oh_id'),
            dqd_id=data.get('dqd_id')
        )
        teams.append(team)
    
    session.bulk_save_objects(teams)
    session.commit()

# 使用
teams_data = [
    {'name': '曼彻斯特联', 'short_name': '曼联', 'oh_id': 'oh_1'},
    {'name': '利物浦', 'short_name': '利物浦', 'oh_id': 'oh_2'},
    {'name': '曼彻斯特城', 'short_name': '曼城', 'oh_id': 'oh_3'},
]
batch_import_teams(session, teams_data)
```

---

## 🔗 **与其他表的关系**

### **1. Team ↔ LeagueSeasonTeam**

```python
# 查询球队参加过的所有联赛赛季
from hyrule_football.models.league_season_team import LeagueSeasonTeam

team_id = 1
seasons = session.query(LeagueSeasonTeam).filter(
    LeagueSeasonTeam.team_id == team_id
).all()

for s in seasons:
    print(f"{s.season} - 联赛ID: {s.league_id}")
```

---

## 📊 **数据示例**

| id | name | short_name | oh_id | dqd_id | is_active |
|----|------|------------|-------|--------|-----------|
| 1 | 曼彻斯特联 | 曼联 | oh_123 | dqd_456 | 1 |
| 2 | 利物浦 | 利物浦 | oh_124 | dqd_457 | 1 |
| 3 | 曼彻斯特城 | 曼城 | oh_125 | dqd_458 | 1 |

---

## ✅ **总结**

✅ **简洁设计**
- 只包含核心字段
- 避免过度设计

✅ **多平台支持**
- `oh_id` 和 `dqd_id` 唯一索引
- 支持平台数据映射

✅ **性能优化**
- 合理的索引设计
- 支持快速查询

✅ **数据完整性**
- 平台ID唯一约束
- 软删除保留历史数据

