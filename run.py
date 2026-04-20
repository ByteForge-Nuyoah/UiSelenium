# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : run.py
# @Desc    : 框架主入口

"""
说明：
1、用例创建原则，测试文件名必须以“test”开头，测试函数必须以“test”开头。
2、运行方式：
  > python run.py  (默认在test环境运行测试用例, 报告采用allure)
  > python run.py -m demo 在test环境仅运行打了标记demo用例， 默认报告采用allure
  > python run.py -env live 在live环境运行测试用例
  > python run.py -env=test 在test环境运行测试用例
  > python run.py -driver chrome  (使用chrome浏览器运行测试用例)
  > python run.py -env test  -report no -driver chrome-headless  在test环境，使用谷歌无头浏览器运行用例，并且生成allure html report
"""

import os
import argparse
import time
import subprocess
import pytest
import schedule
from loguru import logger
from config.settings import LOG_LEVEL, RunConfig, ENV_VARS, RUN_CONFIG_DATA
from config.global_vars import GLOBAL_VARS
from config.path_config import (
    REPORT_DIR,
    LOG_DIR,
    CONF_DIR,
    ALLURE_RESULTS_DIR,
    ALLURE_HTML_DIR,
)
from utils.report.send_result_handle import send_result
from utils.report.allure_handle import generate_allure_report
from utils.report.platform_handle import PlatformHandle
from utils.log_utils import capture_logs


def run(**kwargs):
    """
    框架运行主函数
    :param kwargs: 命令行参数字典
    """
    try:
        # ------------------------ 捕获日志----------------------------
        # 设置日志级别和日志文件路径，capture_logs函数通常用于配置loguru日志记录器
        capture_logs(level=LOG_LEVEL, filename=os.path.join(LOG_DIR, "service.log"))

        logger.info("""
                               _    _         _      _____         _
                __ _ _ __ (_)  / \\  _   _| |_ __|_   _|__  ___| |_
               / _` | "_ \\| | / _ \\| | | | __/ _ \\| |/ _ \\/ __| __|
              | (_| | |_) | |/ ___ \\ |_| | || (_) | |  __/\\__ \\ |_
               \\__,_| .__/|_/_/   \\_\\__,_|\\__\\___/|_|\\___||___/\\__|
                    |_|
                    Starting      ...     ...     ...
                  """)
        # ------------------------ 处理一下获取到的参数----------------------------

        logger.debug(f"打印一下run方法的入参：{kwargs}")

        # ------------------------ 定时任务逻辑 ------------------------
        # 检查是否启用了定时任务模式 (命令行参数优先)
        schedule_mode = kwargs.get("schedule") == "yes"
        cron_config = ENV_VARS.get("cron", {})
        
        # 如果启用了定时任务模式，则进入调度循环
        if schedule_mode:
            run_time = cron_config.get("time", "22:00")
            logger.info(f"已启动定时任务模式，将于每天 {run_time} 执行自动化测试...")
            
            # 定义任务函数
            def job():
                logger.info("⏰ 定时任务触发，开始执行测试...")
                # 递归调用 run 函数执行测试，注意这里不再传递 schedule 参数，避免无限递归
                # 复制 kwargs 并移除 schedule 参数
                job_kwargs = kwargs.copy()
                job_kwargs["schedule"] = "no"
                run(**job_kwargs)
                logger.info("✅ 定时任务执行完毕，等待下一次触发...")

            # 设置定时任务
            schedule.every().day.at(run_time).do(job)
            
            # 阻塞主线程，保持运行
            while True:
                schedule.run_pending()
                time.sleep(1)
            
            # 定时任务模式下，循环不会结束，直接返回
            return

        # 获取浏览器驱动类型，默认为 Edge。这个配置会影响 driver_utils 中浏览器的启动
        RunConfig.driver_type = kwargs.get("driver_type", "Edge")

        # 如果开启了无头模式 (headless=True)，且 driver_type 没有显式指定 headless，则自动追加 -headless 后缀
        # 这样可以确保在配置了 headless 模式下，浏览器确实以无头模式运行
        if RunConfig.headless:
            if (
                RunConfig.driver_type == "chrome"
                and "headless" not in RunConfig.driver_type
            ):
                RunConfig.driver_type = "chrome-headless"
            elif (
                RunConfig.driver_type == "firefox"
                and "headless" not in RunConfig.driver_type
            ):
                RunConfig.driver_type = "firefox-headless"

        # 获取运行环境参数 (test/live)，默认为 test
        env = kwargs.get("env", "test").lower()

        # 根据指定的环境参数，从配置文件中加载对应环境的配置数据 (如 host, db info 等)
        # 并保存到 GLOBAL_VARS 全局变量中，供后续测试代码使用
        ENV_VARS["run"]["env"] = ENV_VARS[env]["host"]
        GLOBAL_VARS.update(ENV_VARS["run"])
        GLOBAL_VARS.update(ENV_VARS[env])

        # 获取 pytest 的标记 (-m) 参数，用于筛选特定的测试用例
        marks = kwargs.get("m", "") or None
        # 获取项目名称，用于支持多项目结构
        project_name = kwargs.get("project", "")
        # 获取具体的测试路径 (文件或目录)
        test_path = kwargs.get("path", "")

        # ------------------------ 设置pytest相关参数 ------------------------
        # 构造 pytest 的启动参数列表
        # --maxfail: 失败多少次后停止运行
        # --reruns: 失败重跑次数
        # --reruns-delay: 重跑间隔时间
        # --alluredir: allure 结果数据的输出目录
        # --clean-alluredir: 运行前清理 allure 结果目录
        arg_list = [
            f"--maxfail={RunConfig.max_fail}",
            f"--reruns={RunConfig.rerun}",
            f"--reruns-delay={RunConfig.reruns_delay}",
            f"--alluredir={ALLURE_RESULTS_DIR}",
            "--clean-alluredir",
        ]

        # 处理项目参数逻辑
        if test_path:
            # 如果指定了具体的测试路径，优先使用
            if not os.path.exists(test_path):
                logger.error(f"指定测试路径不存在: {test_path}")
                return
            arg_list.append(test_path)
        elif project_name:
            # 如果指定了项目名称，则自动定位到该项目的 testcases 目录
            GLOBAL_VARS["project_name"] = project_name
            # 拼接项目测试目录路径：projects/{project_name}/testcases
            project_test_dir = os.path.join("projects", project_name, "testcases")
            if os.path.exists(project_test_dir):
                arg_list.append(project_test_dir)
            else:
                logger.error(
                    f"项目 {project_name} 的测试目录不存在: {project_test_dir}"
                )
                return

        # 如果指定了标记 (-m)，则添加到 pytest 参数中
        if marks:
            arg_list.append(f"-m {marks}")

        # ------------------------ pytest执行测试用例 ------------------------
        # 调用 pytest.main 执行测试
        logger.info(f"开始运行 Pytest，参数列表: {arg_list}")
        pytest.main(args=arg_list)

        # ------------------------ 生成测试报告 ------------------------
        # 如果 report 参数为 yes，则生成 Allure HTML 报告
        if kwargs.get("report") == "yes":
            # generate_allure_report 函数负责将 json 结果转换为 html 报告，并打包成 zip
            report_path, attachment_path = generate_allure_report(
                allure_results=ALLURE_RESULTS_DIR,
                allure_report=ALLURE_HTML_DIR,
                windows_title=ENV_VARS["run"]["项目名称"],
                report_name=ENV_VARS["run"]["报告标题"],
                env_info={"运行环境": ENV_VARS["run"]["env"]},
                attachment_path=os.path.join(REPORT_DIR, f"autotest_report.zip"),
            )
            # ------------------------ 发送测试结果 ------------------------
            # 发送测试结果通知 (钉钉、企业微信、邮件)
            send_result(
                report_info=ENV_VARS["run"],
                report_path=report_path,
                attachment_path=attachment_path,
            )

            # ------------------------ 自动打开报告并延迟关闭 ------------------------
            # 如果是无头模式，默认不自动打开报告，除非显式指定 open=yes
            is_headless = "headless" in RunConfig.driver_type.lower() or RunConfig.headless
            should_open = kwargs.get("open") == "yes"
            
            if should_open and not is_headless:
                try:
                    logger.info("正在启动Allure报告服务...")
                    # 获取 allure 命令的可执行文件路径
                    allure_bin = PlatformHandle().allure
                    # 使用 allure open 命令打开报告
                    cmd = [allure_bin, "open", ALLURE_HTML_DIR]

                    # 启动子进程打开报告服务
                    process = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )

                    logger.info("Allure报告已在浏览器打开，将在20秒后自动关闭服务...")
                    # 等待 20 秒，让用户有时间查看报告
                    time.sleep(20)

                    # 关闭 allure 服务进程
                    process.terminate()
                    logger.info("Allure报告服务已自动关闭")
                except Exception as e:
                    logger.error(f"自动打开报告失败: {e}")

    except Exception as e:
        raise e


if __name__ == "__main__":
    # 定义命令行参数
    parser = argparse.ArgumentParser(description="框架主入口")
    parser.add_argument(
        "-report",
        default=RUN_CONFIG_DATA.get("report", "yes"),
        help="是否生成allure html report，支持如下类型：yes, no",
    )
    parser.add_argument(
        "-open",
        default=RUN_CONFIG_DATA.get("open", "yes"),
        help="是否自动打开allure html report，支持如下类型：yes, no",
    )
    parser.add_argument("-env", default=RUN_CONFIG_DATA.get("env", "test"), help="输入运行环境：test 或 live")
    parser.add_argument(
        "-m", default=RUN_CONFIG_DATA.get("m", None), help="选择需要运行的用例：python.ini配置的名称"
    )
    parser.add_argument(
        "-driver_type",
        default=RUN_CONFIG_DATA.get("driver_type", "chrome"),
        help="浏览器驱动类型配置，支持如下类型：chrome, chrome-headless, firefox, firefox-headless, edge, ie, opera",
    )
    parser.add_argument(
        "-project", default=RUN_CONFIG_DATA.get("project", None), help="指定运行的项目名称，例如: workspace"
    )
    parser.add_argument("-path", default=RUN_CONFIG_DATA.get("path", None), help="指定运行的测试文件或目录")
    parser.add_argument(
        "-schedule", default="no", help="是否开启定时任务模式 (yes/no)"
    )
    args = parser.parse_args()
    run(**vars(args))

"""
pytest相关参数：以下也可通过pytest.ini配置
     --reruns: 失败重跑次数
     --reruns-delay 失败重跑间隔时间
     --count: 重复执行次数
    -v: 显示错误位置以及错误的详细信息
    -s: 等价于 pytest --capture=no 可以捕获print函数的输出
    -q: 简化输出信息
    -m: 运行指定标签的测试用例
    -x: 一旦错误，则停止运行
    --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
    "--reruns=3", "--reruns-delay=2"
    -s：这个选项表示关闭捕获输出，即将输出打印到控制台而不是被 pytest 截获。这在调试测试时很有用，因为可以直接查看打印的输出。

    --cache-clear：这个选项表示在运行测试之前清除 pytest 的缓存。缓存包括已运行的测试结果等信息，此选项可用于确保重新执行所有测试。

    --capture=sys：这个选项表示将捕获标准输出和标准错误输出，并将其显示在 pytest 的测试报告中。

    --self-contained-html：这个选项表示生成一个独立的 HTML 格式的测试报告文件，其中包含了所有的样式和资源文件。这样，您可以将该文件单独保存，在没有其他依赖的情况下查看测试结果。

    --reruns=0：这个选项表示在测试失败的情况下不重新运行测试。如果设置为正整数，例如 --reruns=3，会在测试失败时重新运行测试最多 3 次。

    --reruns-delay=5：这个选项表示重新运行测试的延迟时间，单位为秒。默认情况下，如果使用了 --reruns 选项，pytest 会立即重新执行失败的测试。如果指定了 --reruns-delay，pytest 在重新运行之前会等待指定的延迟时间。

    -p no:faulthandler 是 pytest 的命令行选项之一，用于禁用 pytest 插件 faulthandler。

    faulthandler 是一个 pytest 插件，它用于跟踪和报告 Python 进程中的崩溃和异常情况。它可以在程序遇到严重错误时打印堆栈跟踪信息，并提供一些诊断功能。

    使用 -p no:faulthandler 选项可以禁用 faulthandler 插件的加载和运行。这意味着 pytest 将不会使用该插件来处理和报告崩溃和异常情况。如果您确定不需要 faulthandler 插件的功能，或者遇到与其加载有关的问题，可以使用这个选项来禁用它。

    请注意，-p no:faulthandler 选项只会禁用 faulthandler 插件，其他可能存在的插件仍然会正常加载和运行。如果您想禁用所有插件，可以使用 -p no:all 选项。

 allure相关参数：
    –-alluredir这个选项用于指定存储测试结果的路径
    
-m标记：
    在pytest中，如果需要为-m参数传递多个值，可以使用以下方式：
    
    pytest -m "value1 and value2"
    这里使用双引号将多个值括起来，并使用and关键字连接它们。这将告诉pytest只运行标记为value1和value2的测试。
    
    如果你想要运行标记为value1或value2的测试，可以使用or关键字：
    
    pytest -m "value1 or value2"
    你还可以使用not关键字来排除某个标记。例如，下面的命令将运行除了标记为value1的所有其他测试：
    
    pytest -m "not value1"
    这样，你就可以根据需要在pytest中使用-m参数传递多个值，并根据标记运行相应的测试。
"""
