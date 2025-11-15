"""
日志配置模块

提供统一的日志配置和管理功能
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# 日志格式
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SIMPLE_FORMAT = "%(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# 日期格式
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_log_level() -> int:
    """
    从环境变量获取日志级别

    Returns:
        日志级别（logging.DEBUG, logging.INFO 等）
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    return level_mapping.get(log_level_str, logging.INFO)


def setup_logger(
    name: Optional[str] = None,
    level: Optional[int] = None,
    log_file: Optional[Path] = None,
    format_style: str = "default",
) -> logging.Logger:
    """
    配置并返回一个 logger

    Args:
        name: logger 名称，通常使用 __name__
        level: 日志级别，如果不指定则从环境变量读取
        log_file: 日志文件路径（可选），如果指定则同时输出到文件
        format_style: 格式风格，可选 "default", "simple", "detailed"

    Returns:
        配置好的 logger

    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("这是一条信息")
        >>> logger.debug("这是调试信息")
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 设置日志级别
    if level is None:
        level = get_log_level()
    logger.setLevel(level)

    # 选择格式
    format_mapping = {
        "default": DEFAULT_FORMAT,
        "simple": SIMPLE_FORMAT,
        "detailed": DETAILED_FORMAT,
    }
    log_format = format_mapping.get(format_style, DEFAULT_FORMAT)
    formatter = logging.Formatter(log_format, datefmt=DATE_FORMAT)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（可选）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取一个已配置的 logger

    Args:
        name: logger 名称，通常使用 __name__

    Returns:
        logger 实例

    Example:
        >>> from hyrule_football.utils import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello")
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        return setup_logger(name)

    return logger


def configure_root_logger(
    level: Optional[int] = None,
    log_file: Optional[Path] = None,
) -> None:
    """
    配置根 logger（影响所有模块）

    Args:
        level: 日志级别
        log_file: 日志文件路径

    Example:
        >>> from hyrule_football.utils.logger import configure_root_logger
        >>> configure_root_logger()  # 在应用启动时调用一次
    """
    if level is None:
        level = get_log_level()

    logging.basicConfig(
        level=level,
        format=DEFAULT_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # 添加文件处理器
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, datefmt=DATE_FORMAT))
        logging.getLogger().addHandler(file_handler)
