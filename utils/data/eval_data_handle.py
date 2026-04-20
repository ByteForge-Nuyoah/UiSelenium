# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : eval_data_handle.py
# @Desc    : # 第三方库导入

# 第三方库导入
from loguru import logger


# 将"[1,2,3]" 或者"{'k':'v'}" -> [1,2,3], {'k':'v'}
def eval_data(data):
    """
    执行一个字符串表达式，并返回其表达式的值
    """
    try:
        if hasattr(eval(data), "__call__"):
            return data
        else:
            return eval(data)
    except Exception as e:
        logger.trace(f"{data} --> 该数据不能被eval\n报错：{e}")
        return data
