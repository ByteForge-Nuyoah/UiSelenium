# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : test_my_account.py
# @Desc    :

import pytest
import allure
import os
from loguru import logger
from projects.workspace.pages.login_page import LoginPage
from projects.workspace.pages.my_account_page import MyAccountPage
from utils.data.data_handle import data_handle
from utils.data.yaml_handle import get_yaml_data
from config.global_vars import GLOBAL_VARS
from config.path_config import IMG_DIR

# -------------------------------------------------------------------------
# 加载测试数据
# -------------------------------------------------------------------------
# 从 yaml 文件中读取数据，方便维护
account_data = get_yaml_data("my_account_data.yaml", __file__)
case_common = account_data["case_common"]
update_cases = account_data["my_account_page_update"]


@pytest.mark.account
@allure.epic(case_common["allure_epic"])
@allure.feature(case_common["allure_feature"])
class TestMyAccount:
    """
    模块：个人中心测试
    """

    @allure.story(update_cases["allure_story"])
    @pytest.mark.parametrize(
        "case",
        update_cases["cases"],
        ids=["{}".format(case["title"]) for case in update_cases["cases"]],
    )
    def test_update_info(self, case, login_driver):
        """
        用例：更新个人基本信息（姓名、手机号、邮箱）
        """
        # --- 1. 准备工作 ---
        # 替换数据中的动态变量
        case = data_handle(obj=case, source=GLOBAL_VARS)
        logger.info(f"开始执行用例: {case['title']}")

        # 初始化页面对象
        # 注意：login_driver Fixture 已自动完成登录操作，直接使用即可
        driver = login_driver
        my_account_page = MyAccountPage(driver)

        # --- 2. 执行步骤 ---
        with allure.step("步骤1：填写并保存新的个人信息"):
            logger.info(
                f"更新信息为 -> 姓名:{case['name']}, 手机:{case['phone']}, 邮箱:{case['email']}"
            )
            my_account_page.update_basic_info(
                name=case["name"], phone=case["phone"], email=case["email"]
            )

        # --- 3. 结果验证 ---
        with allure.step("步骤2：验证操作结果"):
            # 截图留存 - 成功截图放在 success 目录下
            driver_name = (
                str(driver).split(".")[2] if hasattr(driver, "__str__") else "chrome"
            )
            success_dir = os.path.join(IMG_DIR, "success", driver_name)

            # 截图并附加到报告中
            my_account_page.screenshot(
                path=success_dir,
                filename="update_info_success.png",
                title="更新成功截图",
            )

            logger.info("更新操作完成")
            # TODO: 建议后续添加更严格的验证，例如读取输入框的值确认是否与输入一致
