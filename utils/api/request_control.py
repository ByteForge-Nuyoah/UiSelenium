# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : request_control.py
# @Desc    : 处理request请求前后的用例数据

# 标准库导入
import json
import os
import http.cookiejar
import copy
import time

# 第三方库导入
from requests import Response
from loguru import logger

# 本地应用/模块导入
from utils.api.base_request import BaseRequest
from utils.data.data_handle import data_handle
from utils.data.extract_data_handle import (
    json_extractor,
    re_extract,
    response_extract,
)
from utils.report.allure_handle import allure_step
from config.path_config import FILES_DIR


# ---------------------------------------- 请求前的数据处理----------------------------------------#
def url_handle(host, url):
    try:
        """
        用例数据中获取到的url(一般是不带host的，个别特殊的带有host，则不进行处理)
        """
        logger.debug(f"url_handle:" f"host={host}\n" f"url={url}")
        # 从用例数据中获取url，如果键url不存在，则返回空字符串
        # 如果url是以http开头的，则直接使用该url，不与host进行拼接
        if url.lower().startswith("http"):
            full_url = url
        else:
            # 如果host以/结尾 并且 url以/开头
            if host.endswith("/") and url.startswith("/"):
                full_url = host[0 : len(host) - 1] + url
            # 如果host以/结尾 并且 url不以/开头
            elif host.endswith("/") and (not url.startswith("/")):
                full_url = host + url
            elif (not host.endswith("/")) and url.startswith("/"):
                # 如果host不以/结尾 且 url以/开头，则将host和url拼接起来，组成新的url
                full_url = host + url
            else:
                # 如果host不以/结尾 且 url不以/开头，则将host和url拼接起来的时候增加/，组成新的url
                full_url = host + "/" + url
        logger.debug(f"处理完成后的full_url：{full_url}")
        return full_url
    except Exception as e:
        logger.debug(f"处理url报错了：{e}")
        raise TypeError(f"处理url报错了：{e}")


class RequestPreDataHandle:
    """
    请求前处理用例数据
    """

    def __init__(self, request_data: dict, global_var: dict):
        logger.debug(
            f"\n======================================================\n"
            "-------------Start：处理用例数据前--------------------\n"
            f"用例标题(title): {type(request_data.get('title', None))} || {request_data.get('title', None)}\n"
            f"用例优先级(severity): {type(request_data.get('severity', None))} || {request_data.get('severity', None)}\n"
            f"请求域名(host): {type(request_data.get('host', None))} || {request_data.get('host', None)}\n"
            f"请求路径(url): {type(request_data.get('url', None))} || {request_data.get('url', None)}\n"
            f"请求方式(method): {type(request_data.get('method', None))} || {request_data.get('method', None)}\n"
            f"请求头(headers):   {type(request_data.get('headers', None))} || {request_data.get('headers', None)}\n"
            f"请求cookies: {type(request_data.get('cookies', None))} || {request_data.get('cookies', None)}\n"
            f"请求类型(request_type): {type(request_data.get('request_type', None))} || {request_data.get('request_type', None)}\n"
            f"请求参数(payload): {type(request_data.get('payload', None))} || {request_data.get('payload', None)}\n"
            f"请求文件(files): {type(request_data.get('files', None))} || {request_data.get('files', None)}\n"
            f"请求后等待(wait_seconds): {type(request_data.get('wait_seconds', None))} || {request_data.get('wait_seconds', None)}\n"
            f"响应断言(assert_response): {type(request_data.get('assert_response', None))} || {request_data.get('assert_response', None)}\n"
            f"数据库断言(assert_sql): {type(request_data.get('assert_sql', None))} || {request_data.get('assert_sql', None)}\n"
            f"后置提取参数(extract): {type(request_data.get('extract', None))} || {request_data.get('extract', None)}\n"
            f"用例依赖(case_dependence): {type(request_data.get('case_dependence', None))} || {request_data.get('case_dependence', None)}\n"
            "====================================================="
        )
        self.request_data = copy.deepcopy(request_data)
        self.global_var = global_var

    def request_data_handle(self):
        """
        针对用例数据进行处理，识别用例数据中的关键字${xxxx}，使用全局变量进行替换或者执行关键字中的方法替换为具体值
        """
        self.url_handle()
        self.method_handle()
        self.headers_handle()
        self.cookies_handle()
        self.payload_handle()
        self.files_handle()
        self.wait_seconds_handle()
        self.assert_handle()
        self.extract_handle()
        logger.debug(
            f"\n======================================================\n"
            "-------------End：处理用例数据后--------------------\n"
            f"用例标题(title):  {type(self.request_data.get('title', None))} || {self.request_data.get('title', None)}\n"
            f"用例优先级(severity): {type(self.request_data.get('severity', None))} || {self.request_data.get('severity', None)}\n"
            f"请求路径(url): {type(self.request_data.get('url', None))} || {self.request_data.get('url', None)}\n"
            f"请求方式(method): {type(self.request_data.get('method', None))} || {self.request_data.get('method', None)}\n"
            f"请求头(headers):   {type(self.request_data.get('headers', None))} || {self.request_data.get('headers', None)}\n"
            f"请求cookies: {type(self.request_data.get('cookies', None))} || {self.request_data.get('cookies', None)}\n"
            f"请求类型(request_type): {type(self.request_data.get('request_type', None))} || {self.request_data.get('request_type', None)}\n"
            f"请求参数(payload): {type(self.request_data.get('payload', None))} || {self.request_data.get('payload', None)}\n"
            f"请求文件(files): {type(self.request_data.get('files', None))} || {self.request_data.get('files', None)}\n"
            f"请求后等待(wait_seconds): {type(self.request_data.get('wait_seconds', None))} || {self.request_data.get('wait_seconds', None)}\n"
            f"响应断言(assert_response): {type(self.request_data.get('assert_response', None))} || {self.request_data.get('assert_response', None)}\n"
            f"数据库断言(assert_sql): {type(self.request_data.get('assert_sql', None))} || {self.request_data.get('assert_sql', None)}\n"
            f"后置提取参数(extract): {type(self.request_data.get('extract', None))} || {self.request_data.get('extract', None)}\n"
            f"用例依赖(case_dependence): {type(self.request_data.get('case_dependence', None))} || {self.request_data.get('case_dependence', None)}\n"
            "====================================================="
        )
        return self.request_data

    def url_handle(self):
        """
        用例数据中获取到的url(一般是不带host的，个别特殊的带有host，则不进行处理)
        """
        # 检测url中是否存在需要替换的参数，如果存在则进行替换
        url = data_handle(
            obj=self.request_data.get("url", None), source=self.global_var
        )
        # 进行url处理，最终得到full_url
        host = self.global_var.get("host", "")
        self.request_data["url"] = url_handle(host, url)

    def method_handle(self):
        # TODO 暂时不需要处理，后续有需要在处理
        pass

    def cookies_handle(self):
        """
        requests模块中，cookies参数要求是Dict or CookieJar object
        """
        cookies = self.request_data.get("cookies", None)

        # 从用例数据中获取cookies， 处理cookies
        if cookies:
            # 通过全局变量替换cookies，得到的是一个str类型
            cookies = data_handle(obj=cookies, source=self.global_var)
            try:
                cookies = json.loads(cookies)
            except Exception as e:
                cookies = cookies
            if isinstance(cookies, dict) or isinstance(
                cookies, http.cookiejar.CookieJar
            ):
                self.request_data["cookies"] = cookies
            else:
                logger.error(
                    f"cookies参数要求是Dict or CookieJar object， 目前cookies类型是：{type(cookies)}， cookies值是：{cookies}"
                )
                raise TypeError(
                    f"cookies参数要求是Dict or CookieJar object， 目前cookies类型是：{type(cookies)}， cookies值是：{cookies}"
                )

    def headers_handle(self):
        """
        headers里面传cookies，要求cookies类型是str
        """
        headers = self.request_data.get("headers", None)

        # 从用例数据中获取header， 处理header
        if headers:
            self.request_data["headers"] = data_handle(
                obj=headers, source=self.global_var
            )
            # 如果请求头中有cookies，需要进行单独处理
            if self.request_data["headers"].get("cookies", None):
                cookies = self.request_data["headers"]["cookies"]
                if isinstance(cookies, dict):
                    # 如果是字典类型，就转成字符串
                    self.request_data["headers"]["cookies"] = json.dumps(cookies)
                else:
                    self.request_data["headers"]["cookies"] = cookies

    def payload_handle(self):
        # 处理请求参数payload
        payload = self.request_data.get("payload", None)
        if payload:
            self.request_data["payload"] = data_handle(
                obj=payload, source=self.global_var
            )

    def files_handle(self):
        """
        格式：接口中文件参数的名称:"文件路径地址"
        例如：{"file": "demo_test_demo.py"}
        """
        # 处理请求参数files参数
        files = self.request_data.get("files", None)
        if files:
            # 支持文件传递${}关键字，将使用data_handle进行处理
            files = data_handle(obj=files, source=self.global_var)
            # 将文件处理成绝对路径
            self.request_data["files"] = os.path.join(FILES_DIR, files)

    def wait_seconds_handle(self):
        """
        处理等待时间参数，如果不能转为int类型，则认为是none
        """
        wait_seconds = self.request_data.get("wait_seconds", None)
        try:
            self.request_data["wait_seconds"] = int(wait_seconds)
        except:
            self.request_data["wait_seconds"] = None

    def assert_handle(self):
        # 处理响应断言参数
        assert_response = self.request_data.get("assert_response", None)
        if assert_response:
            self.request_data["assert_response"] = data_handle(
                obj=assert_response, source=self.global_var
            )
        # 由于数据库断言里面的变量需要请求响应后进行提取，因此目前不进行处理

    def extract_handle(self):
        # 处理提取参数
        extract = self.request_data.get("extract", None)
        if extract:
            self.request_data["extract"] = data_handle(
                obj=extract, source=self.global_var
            )


# ---------------------------------------- 进行请求，请求后的参数提取处理----------------------------------------#
class RequestHandle:
    """
    进行请求，请求后的参数提取处理
    """

    def __init__(self, case_data: dict, global_var: dict):
        self.case_data = case_data
        self.global_var = global_var

    @classmethod
    def api_step_record(cls, **kwargs) -> None:
        """
        在allure/logger中记录请求数据
        """
        key = kwargs.get("id")
        title = kwargs.get("title")
        url = kwargs.get("url")
        method = kwargs.get("method")
        headers = kwargs.get("headers")
        cookies = kwargs.get("cookies")
        request_type = kwargs.get("request_type")
        payload = kwargs.get("payload")
        files = kwargs.get("files")
        wait_seconds = kwargs.get("wait_seconds")
        status_code = kwargs.get("status_code")
        response_result = kwargs.get("response_result")
        response_time_seconds = kwargs.get("response_time_seconds")
        response_time_millisecond = kwargs.get("response_time_millisecond")

        _res = (
            "\n" + "=" * 80 + "\n-------------发送请求--------------------\n"
            f"ID: {key}\n"
            f"标题: {title}\n"
            f"请求URL: {url}\n"
            f"请求方式: {method}\n"
            f"请求头:   {headers}\n"
            f"请求Cookies:   {cookies}\n"
            f"请求关键字: {request_type}\n"
            f"请求参数: {payload}\n"
            f"请求文件: {files}\n"
            f"响应码: {status_code}\n"
            f"响应数据: {response_result}\n"
            f"响应耗时: {response_time_seconds} s || {response_time_millisecond} ms\n"
            + "=" * 80
        )
        logger.info(_res)
        allure_step(f"ID: {key}")
        allure_step(f"标题: {title}")
        allure_step(f"请求URL: {url}")
        allure_step(f"请求方式: {method}")
        allure_step(f"请求头: {headers}")
        allure_step(f"请求Cookies: {cookies}")
        allure_step(f"请求关键字: {request_type}")
        allure_step(f"请求参数: {payload}")
        allure_step(f"请求文件: {files}")
        allure_step(f"请求后等待时间: {wait_seconds}")
        allure_step(f"响应码: {status_code}")
        allure_step(f"响应结果: {response_result}")
        allure_step(
            f"响应耗时: {response_time_seconds} s || {response_time_millisecond} ms"
        )

    def http_request(self):
        """
        发送请求并进行后置参数提取操作
        """
        response = BaseRequest.send_request(self.case_data)
        # 根据配置，增加接口请求等待时间。适应部分调用调用后，需要进行内置数据处理的问题
        logger.debug(f"开始等待")
        if self.case_data["wait_seconds"]:
            time.sleep(self.case_data["wait_seconds"])
        logger.debug(f"结束等待")
        self.case_data["status_code"] = response.status_code
        self.case_data["response_time_seconds"] = round(
            response.elapsed.total_seconds(), 2
        )
        self.case_data["response_time_millisecond"] = round(
            response.elapsed.total_seconds() * 1000, 2
        )

        try:
            self.case_data["response_result"] = response.json()
        except:
            self.case_data["response_result"] = response.text

        self.api_step_record(**self.case_data)

        # 处理数据库断言 - 从全局变量中获取最新值，替换数据库断言中的参数
        if self.case_data.get("assert_sql", None):
            self.case_data["assert_sql"] = data_handle(
                obj=self.case_data["assert_sql"], source=self.global_var
            )
        # 处理请求里面的files，使得日志以及allure中写入的是文件，而不是文件二进制内容
        if self.case_data.get("files", None):
            files = self.case_data["files"]
            if isinstance(files, dict):
                dict_values = list(files.values())[0]
                _file = os.path.join(FILES_DIR, dict_values[0])
                logger.info(f"\n请求文件(files): {type(_file)} || {_file}\n")
        return response


# ---------------------------------------- 请求后的参数提取处理----------------------------------------#
def after_request_extract(response: Response, extract):
    """
    从响应数据中提取请求后的参数，并保存到全局变量中
    :param response: request 响应对象
    :param extract: 需要提取的参数字典 '{"k1": "$.data"}' 或 '{"k1": "data:(.*?)$"}'
    :return:
    """
    logger.debug(
        f"\n================================================================================\n"
        "-------------Start: 提取表达式--------------------\n"
        f"后置提取参数（原）: {extract}\n"
    )
    json_result = {}
    re_result = {}
    response_result = {}
    if extract:
        if extract.get("type_jsonpath"):
            # 如果响应数据是json格式，则将按照json方式对后置提取参数进行处理
            res = response.json()
            for k, v in extract["type_jsonpath"].items():
                json_result[k] = json_extractor(res, v)
            logger.debug(
                "\n-------------从response.json()中通过jsonpath方式提取到的结果--------------------\n"
                f"后置提取参数（新）: {json_result}\n"
            )
        if extract.get("type_re"):
            # 如果响应数据是str格式，则将按照str方式对后置提取参数进行处理
            res = response.text
            for k, v in extract["type_re"].items():
                re_result[k] = data_handle(obj=re_extract(res, v))
            logger.debug(
                "\n-------------从response.text中通过正则表达式提取到的结果--------------------\n"
                f"后置提取参数（新）: {re_result}\n"
            )

        if extract.get("type_response"):
            for k, v in extract["type_response"].items():
                response_result[k] = response_extract(response, v)
            logger.debug(
                "-------------从response中提取到的结果--------------------\n"
                f"后置提取参数（新）: {re_result}\n"
            )
    result = {**json_result, **re_result, **response_result}
    logger.info(
        "\n-------------End：所有提取到的结果--------------------\n"
        f"后置提取参数（新）: {result}\n"
        "================================================================================"
    )
    allure_step(f"参数提取结果：{result}")
    return result
