# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : base_request.py
# @Desc    : # 标准库导入

# 标准库导入
import os
import time

# 第三方库导入
from loguru import logger
import requests  # pip install requests
from requests_toolbelt import MultipartEncoder  # pip install requests_toolbelt

# 本地应用/模块导入


class BaseRequest:
    """
    Request操作封装
    """

    TIMEOUT = 8

    session = None

    @classmethod
    def get_session(cls):
        """
        单例模式保证测试过程中使用的都是一个session对象；
        requests.session可以自动处理cookies，做状态保持。
        """
        if cls.session is None:
            cls.session = requests.Session()  # 创建一个 session
        return cls.session

    @classmethod
    def send_request(cls, req_data):
        """
        处理请求数据，转换成可用数据发送请求
        :param req_data: 请求数据
        :return: 响应对象
        """
        try:

            return cls.send_api_request(
                url=req_data.get("url"),
                method=req_data.get("method").lower(),
                request_type=req_data.get("request_type", None),
                header=req_data.get("headers", None),
                payload=req_data.get("payload", None),
                files=req_data.get("files", None),
                cookies=req_data.get("cookies", None),
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"请求出错，{str(e)}")
            raise ValueError(f"请求出错，{str(e)}")

    @classmethod
    def send_api_request(
        cls,
        url: str,
        method: str,
        request_type: str,
        header=None,
        payload=None,
        files=None,
        cookies=None,
    ):
        """
        发送请求
        :param method: 请求方法
        :param url: 请求url
        :param request_type: 请求参数类型，可选值为params，json，data
        :param payload: 请求数据，对于不同请求类型，可以为dict，MultipartEncoder等
        :param files: 请求上传的文件
        :param header: 请求头
        :param cookies: 请求cookies
        :return: 返回res对象
        """
        headers = header or {}
        session = cls.get_session()
        if request_type:
            if request_type.lower() == "params":
                response = session.request(
                    method=method,
                    url=url,
                    params=payload,
                    headers=headers,
                    cookies=cookies,
                    timeout=cls.TIMEOUT,
                )
                return response
            elif request_type.lower() == "data":
                response = session.request(
                    method=method,
                    url=url,
                    data=payload,
                    headers=headers,
                    cookies=cookies,
                    timeout=cls.TIMEOUT,
                )
                return response
            elif request_type.lower() == "json":
                response = session.request(
                    method=method,
                    url=url,
                    json=payload,
                    headers=headers,
                    cookies=cookies,
                    timeout=cls.TIMEOUT,
                )
                return response
            elif request_type.lower() == "file":
                if files:
                    file_name = os.path.basename(files)
                    fields = payload or "file"
                    encoder = MultipartEncoder(
                        fields={fields: (file_name, open(files, "rb"))},
                        boundary="------------------------" + str(time.time()),
                    )
                    headers["Content-Type"] = encoder.content_type
                    response = session.request(
                        method=method,
                        url=url,
                        data=encoder.to_string(),
                        headers=headers,
                        cookies=cookies,
                        timeout=cls.TIMEOUT,
                    )
                    return response
                else:
                    logger.warning(f"文件为空进行上传！ files={files}")
                    response = session.request(
                        method=method,
                        url=url,
                        files=files,
                        headers=headers,
                        cookies=cookies,
                        timeout=cls.TIMEOUT,
                    )
                    return response
            else:
                logger.error("request_type可选关键字为params, json, data, file")
                raise ValueError("request_type可选关键字为params, json, data, file")
        else:
            logger.error("request_type参数不能为空")
            raise ValueError("request_type参数不能为空")
