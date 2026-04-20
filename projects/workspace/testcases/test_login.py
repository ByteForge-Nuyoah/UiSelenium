# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : test_login.py
# @Desc    : 登录功能测试用例

import pytest
import allure
from loguru import logger
from projects.workspace.pages.login_page import LoginPage
from utils.data.data_handle import data_handle
from utils.data.yaml_handle import get_yaml_data
from config.global_vars import GLOBAL_VARS

# --- 常量定义 ---
DATA_FILE = "login_case_data.yaml"
KEY_CASE_COMMON = "case_common"
KEY_LOGIN_SUCCESS = "login_page_success"

# 加载YAML测试数据
# 注意：get_yaml_data 内部处理了路径，这里传入文件名即可
login_data = get_yaml_data(DATA_FILE, __file__)
case_common = login_data[KEY_CASE_COMMON]
login_success_data = login_data[KEY_LOGIN_SUCCESS]


@pytest.mark.login
@allure.epic(case_common["allure_epic"])
@allure.feature(case_common["allure_feature"])
class TestLogin:

    @allure.story(login_success_data["allure_story"])
    @pytest.mark.parametrize(
        "case",
        login_success_data["cases"],
        ids=[case["title"] for case in login_success_data["cases"]],
    )
    def test_login_success(self, case, login_driver):
        """
        用例：验证用户可以使用正确的用户名和密码成功登录
        login_driver fixture 已自动完成登录，此处验证登录状态
        """
        case_data = data_handle(obj=case, source=GLOBAL_VARS)
        logger.info(f"开始执行用例: {case_data['title']}")

        driver = login_driver
        login_page = LoginPage(driver)

        with allure.step("验证是否已登录成功"):
            is_success = login_page.is_login_success()
            assert is_success, "登录失败：未检测到登录后的主页元素"
