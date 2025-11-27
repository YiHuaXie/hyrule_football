# 日志快速参考

## 1. 导入和创建 Logger

```python
from app.utils import get_logger

logger = get_logger(__name__)
```

## 2. 使用日志

```python
logger.debug("调试信息")      # 详细的调试信息
logger.info("一般信息")       # 确认程序正常运行
logger.warning("警告信息")    # 有潜在问题但程序继续运行
logger.error("错误信息")      # 某个功能失败
logger.critical("严重错误")   # 程序可能无法继续运行
```

## 3. 控制日志级别

### 在 .env 文件中设置

```bash
# 开发环境 - 显示所有日志
LOG_LEVEL=DEBUG

# 生产环境 - 只显示重要信息
LOG_LEVEL=INFO

# 只显示警告和错误
LOG_LEVEL=WARNING
```

### 临时设置（命令行）

```bash
# Linux/macOS
export LOG_LEVEL=DEBUG
python your_script.py

# Windows
set LOG_LEVEL=DEBUG
python your_script.py
```

## 4. 替换现有的 print 语句

| 之前 | 之后 |
|------|------|
| `print(f"值: {value}")` | `logger.debug(f"值: {value}")` |
| `print("✅ 成功")` | `logger.info("✅ 成功")` |
| `print("⚠️ 警告")` | `logger.warning("⚠️ 警告")` |
| `print("❌ 错误")` | `logger.error("❌ 错误")` |

## 5. 日志级别对照表

| 级别 | 何时显示 |
|------|---------|
| DEBUG | `LOG_LEVEL=DEBUG` |
| INFO | `LOG_LEVEL=DEBUG` 或 `LOG_LEVEL=INFO` |
| WARNING | `LOG_LEVEL=DEBUG/INFO/WARNING` |
| ERROR | `LOG_LEVEL=DEBUG/INFO/WARNING/ERROR` |
| CRITICAL | 总是显示 |

## 6. 实际示例

```python
from app.utils import get_logger

logger = get_logger(__name__)

def process_data(data):
    logger.debug(f"输入数据: {data}")  # 调试信息
    
    try:
        result = do_something(data)
        logger.info(f"✅ 处理成功: {result}")  # 成功信息
        return result
    except Exception as e:
        logger.error(f"❌ 处理失败: {e}")  # 错误信息
        raise
```

## 7. 测试不同日志级别

运行示例：

```bash
# 查看所有日志
LOG_LEVEL=DEBUG python examples/logging_example.py

# 只看重要信息
LOG_LEVEL=INFO python examples/logging_example.py

# 只看警告和错误
LOG_LEVEL=WARNING python examples/logging_example.py
```

