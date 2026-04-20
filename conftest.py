# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : conftest.py
# @Desc    : 这是文件的描述信息

# 标准库导入
import re
import time
import os
from datetime import datetime

# 第三方库导入
import pytest
import allure
from loguru import logger

# 本地应用/模块导入
from config.path_config import IMG_DIR, REPORT_DIR
from config.settings import RunConfig
from utils.driver_utils import GetDriver
from utils.report.allure_handle import allure_step
from utils.base_page import BasePage
from utils.data.data_handle import FakerData

# ------------------------------------- START: pytest钩子函数处理---------------------------------------#
_session_start_time = None


def pytest_sessionstart(session):
    global _session_start_time
    _session_start_time = time.time()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """设置列"用例描述"的值为用例的标题title"""
    outcome = yield
    # 获取调用结果的测试报告，返回一个report对象
    # report对象的属性包括when（steup, call, teardown三个值）、nodeid(测试用例的名字)、outcome(用例的执行结果，passed,failed)
    report = outcome.get_result()
    # 将测试用例的title作为测试报告"用例描述"列的值。
    # 注意参数传递时需要这样写：@pytest.mark.parametrize("case", cases, ids=["{}".format(case["title"]) for case in cases])
    report.description = re.findall("\\[(.*?)\\]", report.nodeid)[0]
    report.func = report.nodeid.split("[")[0]
    #  allure-pytest的报错截图添加到报告
    if report.when == "call" or report.when == "setup":
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # 失败截图
            if RunConfig.driver:
                driver = RunConfig.driver
                logger.debug(f"{driver}： 开始进行失败截图操作......")
                # 创建不同浏览器驱动保存截图的目录 - 失败截图放在 fail 目录下
                driver_dir = os.path.join(IMG_DIR, "fail", str(driver).split(".")[2])
                os.makedirs(driver_dir, exist_ok=True)
                parameters = item.callspec.params["case"]
                file_name = (
                    FakerData.remove_special_characters(
                        target=parameters.get("title", "")
                    )
                    + "_"
                    + datetime.now().strftime("%Y-%m-%d %H_%M_%S")
                    + ".png"
                )

                # 截图并保存到本地
                BasePage(driver=driver).screenshot(
                    path=driver_dir, filename=file_name, title="失败截图"
                )
        elif report.passed and report.when == "call":
             if RunConfig.driver and RunConfig.success_screenshot:
                driver = RunConfig.driver
                driver_dir = os.path.join(IMG_DIR, "success", str(driver).split(".")[2])
                os.makedirs(driver_dir, exist_ok=True)
                
                try:
                    parameters = item.callspec.params["case"]
                    title = parameters.get("title", "success_case")
                except Exception:
                    title = "success_case"
                    
                file_name = (
                    FakerData.remove_special_characters(target=title)
                    + "_"
                    + datetime.now().strftime("%Y-%m-%d %H_%M_%S")
                    + ".png"
                )

                BasePage(driver=driver).screenshot(
                    path=driver_dir, filename=file_name, title="成功截图"
                )


def pytest_terminal_summary(terminalreporter, config):
    """
    收集测试结果
    """
    _RERUN = len(
        [i for i in terminalreporter.stats.get("rerun", []) if i.when != "teardown"]
    )
    try:
        # 获取pytest传参--reruns的值
        reruns_value = int(config.getoption("--reruns"))
        _RERUN = int(_RERUN / reruns_value)
    except Exception:
        reruns_value = "未配置--reruns参数"
        _RERUN = len(
            [i for i in terminalreporter.stats.get("rerun", []) if i.when != "teardown"]
        )

    _PASSED = len(
        [i for i in terminalreporter.stats.get("passed", []) if i.when != "teardown"]
    )
    _ERROR = len(
        [i for i in terminalreporter.stats.get("error", []) if i.when != "teardown"]
    )
    _FAILED = len(
        [i for i in terminalreporter.stats.get("failed", []) if i.when != "teardown"]
    )
    _SKIPPED = len(
        [i for i in terminalreporter.stats.get("skipped", []) if i.when != "teardown"]
    )
    _XPASSED = len(
        [i for i in terminalreporter.stats.get("xpassed", []) if i.when != "teardown"]
    )
    _XFAILED = len(
        [i for i in terminalreporter.stats.get("xfailed", []) if i.when != "teardown"]
    )

    _TOTAL = terminalreporter._numcollected

    global _session_start_time
    _DURATION = time.time() - _session_start_time

    session_start_time = datetime.fromtimestamp(_session_start_time)
    _START_TIME = (
        f"{session_start_time.year}年{session_start_time.month}月{session_start_time.day}日 "
        f"{session_start_time.hour}:{session_start_time.minute}:{session_start_time.second}"
    )

    test_info = (
        f"各位同事, 大家好:\n"
        f"自动化用例于 {_START_TIME}- 开始运行，运行时长：{_DURATION:.2f} s， 目前已执行完成。\n"
        f"--------------------------------------\n"
        f"#### 执行结果如下:\n"
        f"- 用例运行总数: {_TOTAL} 个\n"
        f"- 跳过用例个数（skipped）: {_SKIPPED} 个\n"
        f"- 实际执行用例总数: {_PASSED + _FAILED + _XPASSED + _XFAILED} 个\n"
        f"- 通过用例个数（passed）: {_PASSED} 个\n"
        f"- 失败用例个数（failed）: {_FAILED} 个\n"
        f"- 异常用例个数（error）: {_ERROR} 个\n"
        f"- 重跑的用例数(--reruns的值): {_RERUN} ({reruns_value}) 个\n"
    )
    try:
        _RATE = _PASSED / (_TOTAL - _SKIPPED) * 100
        test_result = f"- 用例成功率: {_RATE:.2f} %\n"
        logger.success(f"{test_info}{test_result}")
    except ZeroDivisionError:
        test_result = "- 用例成功率: 0.00 %\n"
        logger.critical(f"{test_info}{test_result}")

    # 这里是方便在流水线里面发送测试结果到钉钉/企业微信的
    with open(
        file=os.path.join(REPORT_DIR, "test_result.txt"), mode="w", encoding="utf-8"
    ) as f:
        f.write(f"{test_info}{test_result}")


# ------------------------------------- END: pytest钩子函数处理---------------------------------------#
