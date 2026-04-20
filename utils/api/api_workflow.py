# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : api_workflow.py
# @Desc    : # 标准库导入

# 标准库导入
import os

# 第三方库导入
import allure
from loguru import logger

# 本地应用/模块导入
from utils.data.yaml_handle import YamlHandle
from utils.api.request_control import (
    RequestPreDataHandle,
    RequestHandle,
    after_request_extract,
)
from utils.file_utils import get_files
from utils.data.eval_data_handle import eval_data
from utils.assertion.assert_control import AssertHandle


def get_api_data(api_file_path: str, key: str = None):
    """
    根据指定的yaml文件路径，以及key值，获取对应的接口
    :param:api_file_path 接口yaml文件路径
    :param:key 对应接口的id
    """
    api_data = []
    if os.path.isdir(api_file_path):
        logger.debug(f"目标路径是一个目录：{api_file_path}")
        api_files = get_files(target=api_file_path, end=".yaml") + get_files(
            target=api_file_path, end=".yml"
        )
        for api_file in api_files:
            api_data.append(YamlHandle(filename=api_file).read_yaml)
    elif os.path.isfile(api_file_path):
        logger.debug(f"目标路径是一个文件：{api_file_path}")
        api_data.append(YamlHandle(filename=api_file_path).read_yaml)

    else:
        logger.error(f"目标路径错误，请检查！api_file_path={api_file_path}")
        return None

    for api in api_data:
        matching_api = next(
            (item for item in api["case_info"] if item["id"] == key), None
        )
        if matching_api:
            logger.info(
                "\n----------匹配到的api----------\n"
                f"类型：{type(matching_api)}"
                f"值：{matching_api}\n"
            )
            return matching_api

    # 在找不到匹配的情况下，返回一个默认值且记录一条错误日志
    logger.warning(f"未找到id为{key}的接口， 返回值是None")
    raise Exception(f"未找到id为{key}的接口， 返回值是None")


def api_work_flow(req_data: dict, source: dict) -> dict:
    """
    请求过程：请求前用例数据处理，发送请求，断言，参数提取
    :param:req_data 接口请求数据
    :param:source 全局变量，保存接口相关变量的实际值， 例如接口中的${login}，会从source中找到key=login的元素进行替换
    """
    with allure.step(f"依赖接口：{req_data['title']}({req_data['id']})"):
        logger.debug(
            f"\n----------------api_work_flow-----------------\n"
            f"接口请求数据：{req_data}\n"
            f"全局变量：{source}\n"
        )
        if req_data:
            extract_result = {}
            api_data = RequestPreDataHandle(
                request_data=req_data, global_var=source
            ).request_data_handle()
            # 发送请求
            response = RequestHandle(
                case_data=api_data, global_var=source
            ).http_request()
            # 进行响应断言
            AssertHandle(
                assert_data=api_data["assert_response"], response=response
            ).assert_handle()
            # 断言成功后进行参数提取
            res = after_request_extract(response, api_data["extract"])
            for k, v in res.items():
                extract_result[k] = eval_data(v)
            return extract_result
        else:
            logger.error(f"接口请求数据不能为空！\n" f"req_data = {req_data}")
            raise f"接口请求数据不能为空！\nreq_data = {req_data}"
