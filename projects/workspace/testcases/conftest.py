# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : conftest.py
# @Desc    : # 标准库导入

# 标准库导入
# 第三方库导入
import pytest
import allure
from loguru import logger

# 本地应用/模块导入
from config.settings import RunConfig
from utils.driver_utils import GetDriver
from utils.report.allure_handle import allure_title, allure_step
from projects.workspace.pages.login_page import LoginPage
from config.global_vars import GLOBAL_VARS
from utils.data.data_handle import data_handle


@pytest.fixture(scope="function", autouse=True)
def case_handle(request):
    """处理用例"""
    logger.debug(
        "\n-----------------------------START-开始执行用例-----------------------------\n"
    )
    case = request.getfixturevalue("case")
    allure_title(case.get("title", ""))

    driver = request.getfixturevalue("init_driver")
    if not _logged_in:
        allure_step(step_title=f"当前运行的浏览器驱动是：{driver}, 清除浏览器缓存")
        logger.debug(f"当前运行的浏览器驱动是：{driver}")
        driver.delete_all_cookies()

    if case.get("run") is None or case.get("run") is False:
        reason = f"{case.get('title')}: 标记了该用例为false，不执行\\n"
        logger.warning(f"{reason}")
        pytest.skip(reason)

    yield case


def pytest_collection_modifyitems(config, items):
    for item in items:
        # 注意这里的"case"需要与@pytest.mark.parametrize("case", cases)中传递的保持一致
        parameters = item.callspec.params["case"]
        # print(f"测试参数：{type(parameters)}     {parameters}")
        if parameters and parameters.get("severity"):
            if parameters["severity"].upper() == "TRIVIAL":
                item.add_marker(allure.severity(allure.severity_level.TRIVIAL))
            elif parameters["severity"].upper() == "MINOR":
                item.add_marker(allure.severity(allure.severity_level.MINOR))
            elif parameters["severity"].upper() == "CRITICAL":
                item.add_marker(allure.severity(allure.severity_level.CRITICAL))
            elif parameters["severity"].upper() == "BLOCKER":
                item.add_marker(allure.severity(allure.severity_level.BLOCKER))
            else:
                item.add_marker(allure.severity(allure.severity_level.NORMAL))
        else:
            item.add_marker(allure.severity(allure.severity_level.NORMAL))


# ------------------------------------- START: 配置浏览器驱动 ---------------------------------------#
_logged_in = False

@pytest.fixture(scope="session")
def init_driver():
    driver = GetDriver(driver_type=RunConfig.driver_type).get_driver()
    RunConfig.driver = driver
    yield driver
    logger.trace(
        "\n-----------------------------END-用例执行结束-----------------------------\n"
    )
    driver.quit()


@pytest.fixture(scope="function")
def login_driver(init_driver, case):
    """
    登录Fixture：执行登录操作并返回driver
    依赖于init_driver和case fixture
    已登录时复用 session，跳过登录步骤
    """
    global _logged_in
    driver = init_driver
    host = GLOBAL_VARS.get("host", "")
    login_page = LoginPage(driver)

    processed_case = data_handle(obj=case, source=GLOBAL_VARS)
    username = processed_case.get("login_user")
    password = processed_case.get("login_password")

    if not _logged_in:
        with allure.step("前置步骤：登录系统"):
            login_page.open_site(host, clear_session=True)

            if username and password:
                login_page.login(username=username, password=password)

                if not login_page.is_login_success():
                    allure.attach(
                        driver.get_screenshot_as_png(),
                        "登录失败截图",
                        allure.attachment_type.PNG,
                    )
                    raise Exception("登录失败，无法进行后续测试")
                
                _logged_in = True
            else:
                logger.warning(
                    "用例数据中未包含登录信息(login_user/login_password)，跳过登录步骤"
                )
    else:
        with allure.step("前置步骤：复用已登录session"):
            login_page.open_site(host, clear_session=False)
            logger.info("已登录，复用session，跳过登录步骤")

    yield driver
