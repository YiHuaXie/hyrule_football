# 日志使用指南

## 快速开始

### 1. 在模块中使用日志

```python
from hyrule_football.utils import get_logger

# 创建 logger（通常在文件顶部）
logger = get_logger(__name__)

# 使用 logger
def my_function():
    logger.debug("这是调试信息")
    logger.info("这是一般信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误")
```

### 2. 控制日志级别

在 `.env` 文件中设置：

```bash
# 开发环境 - 显示所有日志（包括 DEBUG）
LOG_LEVEL=DEBUG

# 生产环境 - 只显示 INFO 及以上
LOG_LEVEL=INFO

# 只显示警告和错误
LOG_LEVEL=WARNING

# 只显示错误
LOG_LEVEL=ERROR

# 完全静默（只显示严重错误）
LOG_LEVEL=CRITICAL
```

或者在命令行中临时设置：

```bash
# Linux/macOS
export LOG_LEVEL=DEBUG
python your_script.py

# Windows
set LOG_LEVEL=DEBUG
python your_script.py
```

## 日志级别说明

| 级别 | 数值 | 何时使用 | 示例 |
|------|------|---------|------|
| DEBUG | 10 | 详细的调试信息，仅开发时使用 | `logger.debug(f"变量值: {value}")` |
| INFO | 20 | 一般信息，确认程序按预期运行 | `logger.info("✅ 数据保存成功")` |
| WARNING | 30 | 警告信息，程序仍能运行但有潜在问题 | `logger.warning("Redis 连接缓慢")` |
| ERROR | 40 | 错误信息，某个功能失败 | `logger.error("保存失败")` |
| CRITICAL | 50 | 严重错误，程序可能无法继续运行 | `logger.critical("数据库连接失败")` |

## 实际使用示例

### 示例 1：在 odds_image_ocr.py 中使用

```python
from hyrule_football.utils import get_logger

logger = get_logger(__name__)

def _hyr_standard_odds(markdown_text: str, opposite_flag: bool):
    logger.debug(f"opposite_flag: {opposite_flag}")  # 调试信息
    
    odds_list = OddsEngine.hyr_standard_odds_from_text(markdown_text)
    logger.info(f"解析出 {len(odds_list)} 条赔率数据")  # 一般信息
    
    if opposite_flag:
        opposite_odds_list = OddsEngine.opposite_hry_standard_odds(odds_list)
        logger.info(f"✅ 生成对立面数据：{len(opposite_odds_list)} 条")
    
    return sorted_odds

def _save_odds_to_redis(odds_list):
    try:
        store = OddsStore()
        store.save_system_odds(system_name, odds_list, merge=True)
        logger.info("✅ 已保存至 Redis")
    except Exception as e:
        logger.error(f"❌ 保存至 Redis 失败：{e}")
        raise
```

### 示例 2：在应用启动时配置（可选）

如果你想在应用启动时统一配置所有模块的日志：

```python
# main.py 或 __init__.py
from hyrule_football.utils import configure_root_logger
from pathlib import Path

# 配置根 logger（只需调用一次）
configure_root_logger(
    log_file=Path("logs/app.log")  # 可选：同时输出到文件
)
```

### 示例 3：不同环境的配置

**开发环境 `.env.development`：**
```bash
LOG_LEVEL=DEBUG
```

**生产环境 `.env.production`：**
```bash
LOG_LEVEL=WARNING
```

## 迁移现有代码

### 替换 print 语句

**之前：**
```python
print(f"opposite_flag: {opposite_flag}")
print(f"✅ 生成对立面数据：{opposite_odds_list}")
print("✅ 已保存至 Redis")
```

**之后：**
```python
from hyrule_football.utils import get_logger

logger = get_logger(__name__)

logger.debug(f"opposite_flag: {opposite_flag}")  # 调试信息
logger.info(f"✅ 生成对立面数据：{len(opposite_odds_list)} 条")  # 一般信息
logger.info("✅ 已保存至 Redis")
```

## 常见问题

### Q: 如何完全关闭日志？

A: 设置 `LOG_LEVEL=CRITICAL` 或更高

### Q: 如何只在开发环境显示调试信息？

A: 在 `.env` 中设置 `LOG_LEVEL=DEBUG`，生产环境设置 `LOG_LEVEL=INFO`

### Q: 如何同时输出到文件和控制台？

A: 使用 `setup_logger` 并指定 `log_file` 参数：

```python
from hyrule_football.utils import setup_logger
from pathlib import Path

logger = setup_logger(
    __name__, 
    log_file=Path("logs/my_module.log")
)
```

### Q: 如何为不同模块设置不同的日志级别？

A: 使用 `setup_logger` 的 `level` 参数：

```python
import logging
from hyrule_football.utils import setup_logger

# 这个模块只显示警告及以上
logger = setup_logger(__name__, level=logging.WARNING)
```

