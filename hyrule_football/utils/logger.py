"""
日志模块
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import TimedRotatingFileHandler
from hyrule_football.config import settings

# -----------------------------
# 日志格式
# -----------------------------
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# -----------------------------
# 工具方法
# -----------------------------
def get_log_level() -> int:
    mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return mapping.get(settings.LOG_LEVEL.upper(), logging.INFO)


# -----------------------------
# 全局 handler 单例缓存
# -----------------------------
_GLOBAL_CONSOLE_HANDLER = None
_GLOBAL_FILE_HANDLER = None


def _get_console_handler(level: int, formatter: logging.Formatter):
    global _GLOBAL_CONSOLE_HANDLER
    if _GLOBAL_CONSOLE_HANDLER is None:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        _GLOBAL_CONSOLE_HANDLER = handler
    return _GLOBAL_CONSOLE_HANDLER


def _get_file_handler(log_file: Path, level: int, formatter: logging.Formatter):
    global _GLOBAL_FILE_HANDLER
    if _GLOBAL_FILE_HANDLER is None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
            utc=False,
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        _GLOBAL_FILE_HANDLER = handler
    return _GLOBAL_FILE_HANDLER


# -----------------------------
# 主 logger 创建入口
# -----------------------------
def get_logger(
    name: Optional[str] = None,
    *,
    log_file: Optional[Path] = None,
    detailed: bool = False,
) -> logging.Logger:
    """
    获取 logger（模块级使用）
    - 永不重复输出
    - 所有模块自动复用全局 handler
    """
    log_level = get_log_level()
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 阻止日志向 root 冒泡（解决重复输出核心）
    logger.propagate = False

    if not logger.handlers:  # 每个 logger 只加一次 handler
        fmt = DETAILED_FORMAT if detailed else DEFAULT_FORMAT
        formatter = logging.Formatter(fmt, datefmt=DATE_FORMAT)

        # 统一 console handler
        console_handler = _get_console_handler(log_level, formatter)
        logger.addHandler(console_handler)

        # 统一 file handler
        if log_file:
            file_handler = _get_file_handler(log_file, log_level, formatter)
            logger.addHandler(file_handler)

    return logger


# -----------------------------
# 根 logger（可选，用于全局脚本）
# -----------------------------
def configure_root_logger(log_file: Optional[Path] = None):
    """配置根 logger（通常脚本/入口 main 使用）"""

    log_level = get_log_level()
    root = logging.getLogger()
    root.setLevel(log_level)
    root.propagate = False  # 防止重复

    fmt = DEFAULT_FORMAT
    formatter = logging.Formatter(fmt, datefmt=DATE_FORMAT)

    if not root.handlers:
        # console
        console_handler = _get_console_handler(log_level, formatter)
        root.addHandler(console_handler)

        # file
        if log_file:
            file_handler = _get_file_handler(log_file, log_level, formatter)
            root.addHandler(file_handler)


def error_msg(source: str, message: str, *, data: dict | None = None) -> dict:
    return {"source": source, "message": message, "data": data}
