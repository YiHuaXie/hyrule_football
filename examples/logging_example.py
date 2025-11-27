"""
日志使用示例

演示如何在项目中使用日志系统
"""

from hyrule_football.utils import get_logger

# 创建 logger
logger = get_logger(__name__)


def example_basic_logging():
    """基础日志示例"""
    logger.debug("这是调试信息 - 只在 LOG_LEVEL=DEBUG 时显示")
    logger.info("这是一般信息 - LOG_LEVEL=INFO 及以下时显示")
    logger.warning("这是警告信息 - LOG_LEVEL=WARNING 及以下时显示")
    logger.error("这是错误信息 - LOG_LEVEL=ERROR 及以下时显示")
    logger.critical("这是严重错误 - 总是显示")


def example_with_variables():
    """带变量的日志示例"""
    user_name = "张三"
    count = 42
    
    logger.debug(f"调试信息：用户={user_name}, 数量={count}")
    logger.info(f"✅ 处理完成，共处理 {count} 条数据")


def example_error_handling():
    """错误处理中的日志示例"""
    try:
        # 模拟一个错误
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"❌ 计算错误：{e}")
        # 如果需要完整的堆栈信息
        logger.exception("详细错误信息：")


def example_function_with_logging():
    """实际函数中的日志使用"""
    logger.info("开始处理数据...")
    
    data = [1, 2, 3, 4, 5]
    logger.debug(f"输入数据：{data}")
    
    result = sum(data)
    logger.info(f"✅ 处理完成，结果：{result}")
    
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("日志示例")
    print("=" * 60)
    print("\n提示：修改 .env 文件中的 LOG_LEVEL 来控制日志输出")
    print("  - LOG_LEVEL=DEBUG   显示所有日志")
    print("  - LOG_LEVEL=INFO    显示 INFO 及以上")
    print("  - LOG_LEVEL=WARNING 只显示警告和错误")
    print("=" * 60)
    print()
    
    print("1. 基础日志示例：")
    example_basic_logging()
    print()
    
    print("2. 带变量的日志：")
    example_with_variables()
    print()
    
    print("3. 错误处理：")
    example_error_handling()
    print()
    
    print("4. 实际函数示例：")
    result = example_function_with_logging()
    print()
    
    print("=" * 60)
    print("示例完成！")
    print("=" * 60)

