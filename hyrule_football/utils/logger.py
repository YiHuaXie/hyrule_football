"""
日志配置模块
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from hyrule_football.config import settings

# -----------------------------
# 日志格式定义
# -----------------------------
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SIMPLE_FORMAT = "%(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# 日期格式
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_log_level() -> int:
    """从环境变量获取日志级别，如果配置不合法则默认 INFO"""

    log_level_str = settings.LOG_LEVEL.upper()  # 获取配置的日志等级字符串
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_mapping.get(log_level_str, logging.INFO)  # 返回对应的 logging 等级


def setup_logger(
    name: Optional[str] = None,
    level: Optional[int] = None,
    log_file: Optional[Path] = None,
    format_style: str = "default",
) -> logging.Logger:
    """
    创建并配置一个 Logger（多模块可复用，避免重复添加 handler）

    Args:
        name: logger 名称，通常使用 __name__
        level: 日志级别，如果不指定则读取配置
        log_file: 日志文件路径
        format_style: 日志格式风格，可选 "default", "simple", "detailed"

    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger(name)  # 获取或创建 logger

    if not level:
        level = get_log_level()  # 如果未指定等级，从配置读取
    logger.setLevel(level)  # 设置 logger 等级

    # -----------------------------
    # 格式选择
    # -----------------------------
    format_mapping = {
        "default": DEFAULT_FORMAT,
        "simple": SIMPLE_FORMAT,
        "detailed": DETAILED_FORMAT,
    }
    log_format = format_mapping.get(format_style, DEFAULT_FORMAT)
    formatter = logging.Formatter(log_format, datefmt=DATE_FORMAT)

    # -----------------------------
    # 控制台 handler
    # -----------------------------
    # 检查是否已存在 StreamHandler 避免重复输出
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # -----------------------------
    # 文件 handler
    # -----------------------------
    if log_file:
        # 创建父目录（不存在则自动创建）
        log_file.parent.mkdir(parents=True, exist_ok=True)
        # 避免重复添加同一路径的文件 handler
        if not any(
            isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == str(log_file)
            for h in logger.handlers
        ):
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)  # 文件等级可以和控制台一致，也可以固定 DEBUG
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取 logger，如果未配置则自动 setup
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
    配置根 logger（影响整个应用的日志输出）

    Args:
        level: 日志等级
        log_file: 可选日志文件路径
    """
    if level is None:
        level = get_log_level()

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # -----------------------------
    # 控制台 handler
    # -----------------------------
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, datefmt=DATE_FORMAT))
        root_logger.addHandler(console_handler)

    # -----------------------------
    # 文件 handler
    # -----------------------------
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        if not any(
            isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == str(log_file)
            for h in root_logger.handlers
        ):
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT, datefmt=DATE_FORMAT))
            file_handler.setLevel(level)
            root_logger.addHandler(file_handler)
