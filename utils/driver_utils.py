# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : driver_utils.py
# @Desc    : 浏览器驱动管理（仅支持本地驱动）

import os
import shutil
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as CH_Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.ie.service import Service as IeService
from selenium.webdriver.chrome import service  # opera浏览器


class GetDriver:
    """
    获取浏览器驱动
    根据driver_type，加载本地浏览器驱动，并返回driver
    :return:driver
    """

    def __init__(self, driver_type: str):
        # 判断drivers_type是不是列表
        if isinstance(driver_type, str) and driver_type in [
            "chrome",
            "chrome-headless",
            "firefox",
            "firefox-headless",
            "edge",
            "ie",
            "opera",
        ]:
            self.driver_type = driver_type
        else:
            logger.error(
                f"driver_type={driver_type}必须是str类型， 且仅支持如下浏览器：chrome, chrome-headless, firefox, firefox-headless, edge, ie, opera"
            )
            raise NameError(f"drivers_type必须是str类型")

    def get_driver(self):
        """
        根据driver_type初始化不同的浏览器驱动
        """

        driver_type = self.driver_type.lower()
        if driver_type == "chrome":
            return self.chrome_driver()

        if driver_type == "chrome-headless":
            return self.chrome_headless_driver()

        if driver_type == "firefox":
            return self.firefox_driver()

        if driver_type == "firefox-headless":
            return self.firefox_headless_driver()

        if driver_type == "edge":
            return self.edge_driver()

        if driver_type == "ie":
            return self.ie_driver()

        if driver_type == "opera":
            return self.opera_driver()

    def _get_local_driver_path(self, driver_name):
        """
        获取本地 webdriver 目录下的驱动路径
        :param driver_name: 驱动文件名，如 chromedriver
        :return: 驱动绝对路径 或 None（让 Selenium Manager 自动管理）
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        driver_path = os.path.join(project_root, "local_drivers", driver_name)

        if not os.path.exists(driver_path):
            logger.info(f"本地驱动文件不存在: {driver_path}，将使用 Selenium Manager 自动获取")
            return None

        # 确保有执行权限
        try:
            os.chmod(driver_path, 0o755)
        except Exception as e:
            logger.warning(f"无法修改驱动文件权限: {e}")

        logger.info(f"使用本地驱动: {driver_path}")
        return driver_path

    def _build_service(self, service_class, driver_name, env=None, service_args=None):
        """
        构建 Service 对象，智能处理本地驱动和 Selenium Manager
        :param service_class: Service 类 (ChromeService, FirefoxService 等)
        :param driver_name: 驱动文件名
        :param env: 环境变量字典
        :param service_args: Service 参数列表
        :return: Service 实例
        """
        driver_path = self._get_local_driver_path(driver_name)
        
        # 如果本地驱动存在，使用指定路径的 Service
        if driver_path:
            return service_class(
                executable_path=driver_path,
                env=env or {},
                service_args=service_args or []
            )
        
        # 本地驱动不存在时，不指定 executable_path，让 Selenium Manager 自动管理
        logger.info("使用 Selenium Manager 自动下载和管理驱动")
        if env or service_args:
            return service_class(env=env or {}, service_args=service_args or [])
        return service_class()

    def chrome_driver(self):
        """
        chrome浏览器，有头模式
        """
        options = Options()
        # 去掉"chrome正受到自动化测试软件的控制"的提示条
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Add robust options to prevent crashes in restricted environments
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-gpu-shader-disk-cache")
        
        # 禁用 Crashpad 和其他噪音
        options.add_argument("--disable-crash-reporter")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-metrics")
        options.add_argument("--disable-metrics-repo")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-service-autorun")
        options.add_argument("--disable-search-engine-choice-screen")
        
        # Isolation options
        options.add_argument("--use-mock-keychain")
        options.add_argument("--password-store=basic")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-infobars")
        
        # Disable background updates and networking
        options.add_argument("--disable-component-update")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-extensions")
        
        # Comprehensive feature disable
        options.add_argument("--disable-features=Translate,OptimizationHints,MediaRouter,DialMediaRouteProvider,CrashReporter,Crashpad,MetricsReporting,OptimizationGuideModelDownloading,OptimizationHintsFetching")
        
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")  # 只显示 fatal errors

        # Define user data directory in project root to avoid sandbox issues
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        user_data_dir = os.path.join(project_root, '.chrome_user_data')
        
        # Ensure directories exist
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
            
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument(f"--crash-dumps-dir={os.path.join(user_data_dir, 'Crashpad')}")

        # 使用本地 webdriver 目录下的驱动
        # Force HOME and other vars to user_data_dir to prevent access to system directories
        env = os.environ.copy()
        env["HOME"] = user_data_dir
        env["CHROME_USER_DATA_DIR"] = user_data_dir
        env["XDG_CONFIG_HOME"] = user_data_dir
        env["XDG_CACHE_HOME"] = user_data_dir
        
        # Redirect temp directories
        temp_dir = os.path.join(user_data_dir, 'tmp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        env["TMPDIR"] = temp_dir
        env["TEMP"] = temp_dir
        env["TMP"] = temp_dir

        service = self._build_service(
            ChromeService, 
            "chromedriver", 
            env=env,
            service_args=["--disable-build-check", "--verbose", f"--log-path={os.path.join(user_data_dir, 'chromedriver.log')}"]
        )
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        driver.implicitly_wait(3)
        driver.delete_all_cookies()
        return driver

    def chrome_headless_driver(self):
        """
        chrome headless(无头)模式
        """
        # 参数说明，参考地址：https://github.com/GoogleChrome/chrome-launcher/blob/master/docs/chrome-flags-for-tools.md#--enable-automation
        chrome_option = CH_Options()
        chrome_option.add_argument("--headless")
        chrome_option.add_argument("--window-size=1920x1080")
        
        # Add robust options to prevent crashes in restricted environments
        chrome_option.add_argument("--no-sandbox")
        chrome_option.add_argument("--disable-dev-shm-usage")
        chrome_option.add_argument("--disable-gpu")
        chrome_option.add_argument("--disable-gpu-shader-disk-cache")
        
        # 禁用 Crashpad 和其他噪音
        chrome_option.add_argument("--disable-crash-reporter")
        chrome_option.add_argument("--disable-breakpad")
        chrome_option.add_argument("--disable-metrics")
        chrome_option.add_argument("--disable-metrics-repo")
        chrome_option.add_argument("--disable-client-side-phishing-detection")
        chrome_option.add_argument("--no-first-run")
        chrome_option.add_argument("--no-default-browser-check")
        chrome_option.add_argument("--no-service-autorun")
        chrome_option.add_argument("--disable-search-engine-choice-screen")
        
        # Isolation options
        chrome_option.add_argument("--use-mock-keychain")
        chrome_option.add_argument("--password-store=basic")
        chrome_option.add_argument("--disable-domain-reliability")
        chrome_option.add_argument("--disable-renderer-backgrounding")
        chrome_option.add_argument("--disable-infobars")
        
        # Disable background updates and networking
        chrome_option.add_argument("--disable-component-update")
        chrome_option.add_argument("--disable-background-networking")
        chrome_option.add_argument("--disable-sync")
        chrome_option.add_argument("--disable-default-apps")
        chrome_option.add_argument("--disable-extensions")
        
        # Comprehensive feature disable
        chrome_option.add_argument("--disable-features=Translate,OptimizationHints,MediaRouter,DialMediaRouteProvider,CrashReporter,Crashpad,MetricsReporting,OptimizationGuideModelDownloading,OptimizationHintsFetching")
        
        chrome_option.add_argument("--disable-logging")
        chrome_option.add_argument("--log-level=3")

        # Define user data directory in project root to avoid sandbox issues
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        user_data_dir = os.path.join(project_root, '.chrome_user_data_headless')
        
        # Ensure directories exist
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
            
        chrome_option.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_option.add_argument(f"--crash-dumps-dir={os.path.join(user_data_dir, 'Crashpad')}")

        # 使用本地 webdriver 目录下的驱动
        # Force HOME and other vars to user_data_dir to prevent access to system directories
        env = os.environ.copy()
        env["HOME"] = user_data_dir
        env["CHROME_USER_DATA_DIR"] = user_data_dir
        env["XDG_CONFIG_HOME"] = user_data_dir
        env["XDG_CACHE_HOME"] = user_data_dir
        
        # Redirect temp directories
        temp_dir = os.path.join(user_data_dir, 'tmp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        env["TMPDIR"] = temp_dir
        env["TEMP"] = temp_dir
        env["TMP"] = temp_dir
        
        service = self._build_service(
            ChromeService, 
            "chromedriver", 
            env=env,
            service_args=["--disable-build-check", "--verbose", f"--log-path={os.path.join(user_data_dir, 'chromedriver.log')}"]
        )
        driver = webdriver.Chrome(service=service, options=chrome_option)
        driver.implicitly_wait(10)
        driver.delete_all_cookies()  # 清除浏览器所有缓存
        return driver

    def firefox_driver(self):
        """
        firefox浏览器，有头模式
        """
        service = self._build_service(FirefoxService, "geckodriver")
        driver = webdriver.Firefox(service=service)
        driver.maximize_window()
        driver.implicitly_wait(10)
        driver.delete_all_cookies()  # 清除浏览器所有缓存
        return driver

    def firefox_headless_driver(self):
        """
        firefox headless(无头)模式
        """
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--disable-gpu")

        service = self._build_service(FirefoxService, "geckodriver")
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.implicitly_wait(10)
        driver.delete_all_cookies()  # 清除浏览器所有缓存
        return driver

    def edge_driver(self):
        """
        Edge浏览器
        """
        edge_options = webdriver.EdgeOptions()
        edge_options.use_chromium = True
        # 屏蔽inforbar
        edge_options.add_experimental_option("useAutomationExtension", False)
        edge_options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

        service = self._build_service(EdgeService, "msedgedriver")
        driver = webdriver.Edge(service=service, options=edge_options)
        driver.maximize_window()
        driver.implicitly_wait(10)
        driver.delete_all_cookies()  # 清除浏览器所有缓存
        return driver

    def ie_driver(self):
        """
        微软IE浏览器
        """
        ie_options = webdriver.IeOptions()
        service = self._build_service(IeService, "IEDriverServer")
        driver = webdriver.Edge(service=service, options=ie_options)
        driver.maximize_window()
        driver.implicitly_wait(10)
        driver.delete_all_cookies()  # 清除浏览器所有缓存
        return driver

    def opera_driver(self):
        """
        opera浏览器
        """
        webdriver_service = self._build_service(service.Service, "operadriver")
        webdriver_service.start()
        options = webdriver.ChromeOptions()
        options.add_experimental_option("w3c", True)
        driver = webdriver.Remote(webdriver_service.service_url, options=options)
        driver.maximize_window()
        driver.implicitly_wait(10)
        driver.delete_all_cookies()
        return driver
