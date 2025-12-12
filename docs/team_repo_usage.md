# TeamRepo 使用文档

## 📋 **概述**

`TeamRepo` 是球队表的数据访问层（Repository），提供了完整的 CRUD 操作和查询方法。

---

## 🔧 **基础 CRUD 操作**

### **1. 创建球队**

```python
from hyrule_football.database import db_session
from hyrule_football.repositories.team_repo import TeamRepo

with db_session() as db:
    # 创建球队（如果名称已存在则返回现有记录）
    team = TeamRepo.create(
        db,
        name="曼彻斯特联",
        oh_id="oh_team_123",
        dqd_id="dqd_team_456"
    )
    db.commit()
    print(f"创建球队: {team.name}, ID: {team.id}")
```

### **2. 获取或创建球队**

```python
with db_session() as db:
    # 如果存在则返回，不存在则创建
    team = TeamRepo.get_or_create(
        db,
        name="利物浦",
        oh_id="oh_team_124",
        dqd_id="dqd_team_457"
    )
    db.commit()
```

### **3. 按 ID 查询**

```python
with db_session() as db:
    team = TeamRepo.get_by_id(db, team_id=1)
    if team:
        print(f"找到球队: {team.name}")
```

### **4. 按名称查询**

```python
with db_session() as db:
    team = TeamRepo.get_by_name(db, name="曼彻斯特联")
    if team:
        print(f"找到球队: {team.name}, 欧核ID: {team.oh_id}")
```

### **5. 按平台ID查询**

```python
with db_session() as db:
    # 按欧核ID查询
    team = TeamRepo.get_by_oh_id(db, oh_id="oh_team_123")
    
    # 按懂球帝ID查询
    team = TeamRepo.get_by_dqd_id(db, dqd_id="dqd_team_456")
```

### **6. 更新球队信息**

```python
with db_session() as db:
    # 更新多个字段
    team = TeamRepo.update(
        db,
        team_id=1,
        name="曼联",
        oh_id="oh_team_new_123"
    )
    db.commit()
    
    # 只更新欧核ID
    team = TeamRepo.update_oh_id(db, team_id=1, oh_id="oh_team_new_123")
    db.commit()
    
    # 只更新懂球帝ID
    team = TeamRepo.update_dqd_id(db, team_id=1, dqd_id="dqd_team_new_456")
    db.commit()
```

### **7. 删除球队**

```python
with db_session() as db:
    success = TeamRepo.delete(db, team_id=1)
    if success:
        db.commit()
        print("删除成功")
```

---

## 🔍 **查询操作**

### **1. 获取所有球队**

```python
with db_session() as db:
    teams = TeamRepo.get_all(db)
    print(f"共有 {len(teams)} 支球队")
```

### **2. 按平台数据筛选**

```python
with db_session() as db:
    # 获取所有有欧核数据的球队
    teams_with_oh = TeamRepo.get_teams_with_oh(db)
    
    # 获取所有有懂球帝数据的球队
    teams_with_dqd = TeamRepo.get_teams_with_dqd(db)
    
    # 获取同时有两个平台数据的球队
    teams_with_both = TeamRepo.get_teams_with_both(db)
```

### **3. 查找缺少平台数据的球队**

```python
with db_session() as db:
    # 缺少欧核ID的球队
    teams_missing_oh = TeamRepo.get_teams_missing_oh(db)
    print(f"缺少欧核ID的球队: {len(teams_missing_oh)} 支")
    
    # 缺少懂球帝ID的球队
    teams_missing_dqd = TeamRepo.get_teams_missing_dqd(db)
    print(f"缺少懂球帝ID的球队: {len(teams_missing_dqd)} 支")
```

### **4. 模糊搜索**

```python
with db_session() as db:
    # 搜索名称包含"曼"的球队
    teams = TeamRepo.search_by_name(db, keyword="曼")
    for team in teams:
        print(f"- {team.name}")
    # 输出: 曼联, 曼城
```

---

## 📊 **统计操作**

```python
with db_session() as db:
    # 统计球队总数
    total = TeamRepo.count_all(db)
    print(f"球队总数: {total}")
    
    # 统计有欧核数据的球队数量
    count_oh = TeamRepo.count_with_oh(db)
    print(f"有欧核数据: {count_oh}")
    
    # 统计有懂球帝数据的球队数量
    count_dqd = TeamRepo.count_with_dqd(db)
    print(f"有懂球帝数据: {count_dqd}")
    
    # 统计同时有两个平台数据的球队数量
    count_both = TeamRepo.count_with_both(db)
    print(f"同时有两个平台数据: {count_both}")
```

---

## 🚀 **批量操作**

### **批量创建球队**

```python
with db_session() as db:
    teams_data = [
        {"name": "曼联", "oh_id": "oh_123", "dqd_id": "dqd_456"},
        {"name": "利物浦", "oh_id": "oh_124", "dqd_id": "dqd_457"},
        {"name": "曼城", "oh_id": "oh_125", "dqd_id": None},
        {"name": "切尔西", "oh_id": None, "dqd_id": "dqd_458"},
    ]
    
    teams = TeamRepo.batch_create(db, teams_data)
    db.commit()
    print(f"批量创建了 {len(teams)} 支球队")
```

---

## 💡 **完整示例：数据导入流程**

```python
from hyrule_football.database import db_session
from hyrule_football.repositories.team_repo import TeamRepo

def import_teams_from_platform():
    """从平台导入球队数据"""
    
    # 模拟从API获取的数据
    platform_teams = [
        {"name": "曼联", "oh_id": "oh_123", "dqd_id": "dqd_456"},
        {"name": "利物浦", "oh_id": "oh_124", "dqd_id": "dqd_457"},
    ]
    
    with db_session() as db:
        # 批量创建
        teams = TeamRepo.batch_create(db, platform_teams)
        db.commit()
        
        # 统计
        print(f"✅ 导入完成！")
        print(f"  - 球队总数: {TeamRepo.count_all(db)}")
        print(f"  - 有欧核数据: {TeamRepo.count_with_oh(db)}")
        print(f"  - 有懂球帝数据: {TeamRepo.count_with_dqd(db)}")
        print(f"  - 同时有两个平台: {TeamRepo.count_with_both(db)}")

if __name__ == "__main__":
    import_teams_from_platform()
```

---

## ✅ **方法列表**

| 方法 | 说明 |
|------|------|
| `get_by_id(db, team_id)` | 根据ID获取球队 |
| `get_by_name(db, name)` | 根据名称获取球队 |
| `get_by_oh_id(db, oh_id)` | 根据欧核ID获取球队 |
| `get_by_dqd_id(db, dqd_id)` | 根据懂球帝ID获取球队 |
| `create(db, name, oh_id, dqd_id)` | 创建球队（存在则返回） |
| `get_or_create(db, name, oh_id, dqd_id)` | 获取或创建球队 |
| `update(db, team_id, **kwargs)` | 更新球队信息 |
| `update_oh_id(db, team_id, oh_id)` | 更新欧核ID |
| `update_dqd_id(db, team_id, dqd_id)` | 更新懂球帝ID |
| `delete(db, team_id)` | 删除球队 |
| `get_all(db)` | 获取所有球队 |
| `get_teams_with_oh(db)` | 获取有欧核数据的球队 |
| `get_teams_with_dqd(db)` | 获取有懂球帝数据的球队 |
| `get_teams_with_both(db)` | 获取同时有两个平台数据的球队 |
| `get_teams_missing_oh(db)` | 获取缺少欧核ID的球队 |
| `get_teams_missing_dqd(db)` | 获取缺少懂球帝ID的球队 |
| `search_by_name(db, keyword)` | 按名称模糊搜索 |
| `batch_create(db, teams_data)` | 批量创建球队 |
| `count_all(db)` | 统计球队总数 |
| `count_with_oh(db)` | 统计有欧核数据的数量 |
| `count_with_dqd(db)` | 统计有懂球帝数据的数量 |
| `count_with_both(db)` | 统计同时有两个平台数据的数量 |

