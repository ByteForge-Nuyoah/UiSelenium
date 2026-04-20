# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : log_utils.py
# @Desc    : 日志处理

import sys
from loguru import logger


def capture_logs(filename, level="TRACE", filter_type=None):
    """
    日志处理
    文档参考：https://zhuanlan.zhihu.com/p/429452898
    
    日志级别，从低到高：
    logger.trace()   等级5
    logger.debug()   等级10
    logger.info()   等级20
    logger.success()   等级25
    logger.warning()   等级30
    logger.error()   等级40
    logger.critical()   等级50
    
    :param filename: 日志文件名
    :param filter_type: 日志过滤，如：将日志级别为ERROR的单独记录到一个文件中
    :param level: 日志级别设置
    """
    valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
    
    if level.upper() not in valid_levels:
        logger.error(
            f"level={level}, 值错误\n"
            f"level的可选值是：{valid_levels}\n"
            f"将默认level=INFO收集日志"
        )
        level = "INFO"

    logger.remove()

    file_config = {
        "sink": filename,
        "rotation": "10 MB",
        "retention": "3 days",
        "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}.{function}:{line} | {message}",
        "encoding": "utf-8",
        "level": level,
        "enqueue": True,
    }
    
    if filter_type:
        file_config["filter"] = lambda x: filter_type in str(x["level"]).upper()

    logger.add(**file_config)

    console_format = (
        "<dim>{time:YYYY-MM-DD HH:mm:ss}</dim> | "
        "<level>{level: <8}</level> | "
        "<cyan>{module}</cyan>.<dim>{function}</dim>:<yellow>{line}</yellow> | "
        "<level>{message}</level>"
    )

    logger.add(
        sink=sys.stderr,
        level=level,
        format=console_format,
        colorize=True,
    )