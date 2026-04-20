# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : case_dependence.py
# @Desc    : # 第三方库导入

# 第三方库导入
import allure
from loguru import logger

# 本地应用/模块导入
from utils.api.api_workflow import get_api_data, api_work_flow
from utils.data.data_handle import data_handle
from config.path_config import INTERFACE_DIR
from config.global_vars import GLOBAL_VARS


def case_dependence_handle(case_dependence, source):
    """
    处理用例依赖，支持接口依赖，环境变量依赖，SQL依赖。关键字：interface, sql, env_vars
    先处理环境变量依赖，再处理接口依赖，最后处理SQL依赖
    """
    if case_dependence is None:
        logger.debug(f"跳过用例依赖处理 --> case_dependence={case_dependence}")
        return
    # 环境变量处理
    if case_dependence.get("env_vars"):
        if isinstance(case_dependence["env_vars"], dict):
            for key, value in case_dependence["env_vars"].items():
                new_value = data_handle(value, GLOBAL_VARS)
                with allure.step(f"依赖环境变量 --> {key}={new_value}"):
                    GLOBAL_VARS.update({key: new_value})
        else:
            logger.warning(
                f"依赖环境变量格式错误，跳过依赖环境变量处理~ --> env_vars仅支持dict格式"
            )
    else:
        logger.warning(f"依赖环境变量为空，跳过依赖环境变量处理~")
    if case_dependence.get("interface"):
        interfaces = case_dependence["interface"]
        if isinstance(interfaces, str):
            api_data = get_api_data(api_file_path=INTERFACE_DIR, key=interfaces)
            with allure.step(f"依赖接口：{api_data['title']}({interfaces})"):
                result = api_work_flow(req_data=api_data, source=source)
                GLOBAL_VARS.update(result)

        elif isinstance(interfaces, list):
            for interface in interfaces:
                api_data = get_api_data(api_file_path=INTERFACE_DIR, key=interface)
                with allure.step(f"依赖接口：{api_data['title']}({interface})"):
                    result = api_work_flow(req_data=api_data, source=source)
                    GLOBAL_VARS.update(result)
        else:
            logger.warning(
                f"依赖接口格式错误，跳过依赖接口处理~ --> interface 仅支持str和list格式"
            )

    else:
        logger.warning(f"依赖接口为空，跳过依赖接口处理~")

    # 依赖SQL处理
    if case_dependence.get("sql"):
        logger.warning(f"暂时不支持依赖sql处理，后续更新")
        pass
