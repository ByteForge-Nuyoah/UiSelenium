# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : settings.py
# @Desc    : 项目配置文件

import os
import sys
import yaml
from config.path_config import CONF_DIR, PROJECTS_DIR


# ------------------------------------ 测试数据配置 ----------------------------------------------------#
def load_env_config():
    """加载环境配置文件"""
    # 简单的命令行参数解析，获取 -project 参数
    project_name = None
    if "-project" in sys.argv:
        try:
            idx = sys.argv.index("-project")
            if idx + 1 < len(sys.argv):
                project_name = sys.argv[idx + 1]
        except ValueError:
            pass
            
    # 默认使用全局配置
    config_path = os.path.join(CONF_DIR, "default_config.yaml")
    
    # 如果指定了项目，优先查找项目下的配置
    if project_name:
        project_config_path = os.path.join(PROJECTS_DIR, project_name, "config", "project_config.yaml")
        if os.path.exists(project_config_path):
            config_path = project_config_path
            
    if not os.path.exists(config_path):
        # 如果找不到yaml配置，回退到默认配置或报错
        # 这里为了兼容性，可以暂时保留硬编码作为fallback，或者直接报错
        # 既然是重构，我们直接读取YAML
        raise FileNotFoundError(f"配置文件未找到: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 加载配置到 ENV_VARS
try:
    ENV_VARS = load_env_config()
except Exception as e:
    print(f"加载配置文件失败: {e}")
    ENV_VARS = {}

# 加载运行配置
RUN_CONFIG_DATA = ENV_VARS.get("run", {})
PUBLIC_CONFIG_DATA = ENV_VARS.get("public", {})


# ------------------------------------ pytest相关配置 ----------------------------------------------------#
class RunConfig:
    """
    运行测试配置
    """

    # 浏览器类型（不需要修改）
    driver_type = RUN_CONFIG_DATA.get("driver_type", "chrome")
    # 浏览器驱动对象（不需要修改）
    driver = None

    # 失败重跑次数
    rerun = RUN_CONFIG_DATA.get("rerun", 0)

    # 失败重跑间隔时间
    reruns_delay = RUN_CONFIG_DATA.get("reruns_delay", 5)

    # 当达到最大失败数，停止执行
    max_fail = str(RUN_CONFIG_DATA.get("max_fail", "10"))

    # 是否开启无头模式
    headless = RUN_CONFIG_DATA.get("headless", False)

    # 定时任务配置
    cron = RUN_CONFIG_DATA.get("cron", {"enabled": False, "time": "22:00"})

    # 成功截图配置
    success_screenshot = RUN_CONFIG_DATA.get("success_screenshot", False)


# ------------------------------------ 配置信息 ----------------------------------------------------#
# 0表示默认不发送任何通知， 1代表钉钉通知，2代表企业微信通知， 3代表邮件通知， 4代表所有途径都发送通知
SEND_RESULT_TYPE = PUBLIC_CONFIG_DATA.get("send_result_type", 0)

# 指定日志收集级别
LOG_LEVEL = PUBLIC_CONFIG_DATA.get("log_level", "INFO")
"""
支持的日志级别：
    TRACE: 最低级别的日志级别，用于详细追踪程序的执行。
    DEBUG: 用于调试和开发过程中打印详细的调试信息。
    INFO: 提供程序执行过程中的关键信息。
    SUCCESS: 用于标记成功或重要的里程碑事件。
    WARNING: 表示潜在的问题或不符合预期的情况，但不会导致程序失败。
    ERROR: 表示错误和异常情况，但程序仍然可以继续运行。
    CRITICAL: 表示严重的错误和异常情况，可能导致程序崩溃或无法正常运行。
"""

# ------------------------------------ 邮件配置信息 ----------------------------------------------------#

# 发送邮件的相关配置信息
email = PUBLIC_CONFIG_DATA.get("email", {})

# ------------------------------------ 邮件通知内容 ----------------------------------------------------#
_notification = PUBLIC_CONFIG_DATA.get("notification", {})
email_subject = _notification.get("email_subject", "UI自动化报告")
email_content = _notification.get("email_content", "")

# ------------------------------------ 钉钉相关配置 ----------------------------------------------------#
ding_talk = PUBLIC_CONFIG_DATA.get("ding_talk", {})

# ------------------------------------ 钉钉通知内容 ----------------------------------------------------#
ding_talk_title = _notification.get("ding_talk_title", "UI自动化报告")
ding_talk_content = _notification.get("ding_talk_content", "")

# ------------------------------------ 企业微信相关配置 ----------------------------------------------------#
wechat = PUBLIC_CONFIG_DATA.get("wechat", {})

# ------------------------------------ 企业微信通知内容 ----------------------------------------------------#
wechat_content = _notification.get("wechat_content", "")
