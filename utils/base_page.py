# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : base_page.py
# @Desc    : UI自动化测试的一些基础浏览器操作方法

import os
import allure
import time
from functools import wraps
from loguru import logger
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from config.path_config import IMG_DIR


def capture_evidence(func):
    """
    装饰器：操作失败自动截图并记录日志
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            # 获取当前方法名作为操作描述
            action = func.__name__
            logger.error(f"执行 {action} 失败: {e}")

            # 截图
            try:
                timestamp = time.strftime("%Y-%m-%d_%H_%M_%S")
                # 尝试获取 driver，self 是 BasePage 实例，应该有 driver 属性
                if hasattr(self, "driver"):
                    screenshot_content = self.driver.get_screenshot_as_png()
                    allure.attach(
                        screenshot_content,
                        f"失败截图_{action}_{timestamp}",
                        allure.attachment_type.PNG,
                    )
                    logger.info(f"已捕获失败截图: {action}")
            except Exception as s_e:
                logger.warning(f"截图失败: {s_e}")

            raise e

    return wrapper


class BasePage:
    """
    UI自动化基础操作封装
    """

    def __init__(self, driver):
        self.driver = driver

    @capture_evidence
    @allure.step("____访问 - {url}")
    def visit(self, url: str) -> None:
        """
        访问页面
        :param url:
        :return:
        """
        logger.info(f"访问 - {url}")
        self.driver.get(url)

    @capture_evidence
    @allure.step("____刷新页面")
    def refresh(self) -> None:
        """刷新网页"""
        logger.info("刷新页面")
        self.driver.refresh()

    @capture_evidence
    @allure.step("____点击 - {locator}")
    def click(self, locator: tuple, force: bool = False) -> None:
        """
        鼠标点击，当元素不可点击的时候，使用强制点击
        :param locator: 元素（定位方式，定位表达式）
        :param force: 强制点击，默认false
        :return: self
        """
        # 确保元素可见再点击
        elem = self.wait_element_visible(locator)
        if not force:
            logger.info(f"点击 - {locator}")
            try:
                elem.click()
            except Exception as e:
                logger.warning(f"常规点击失败，尝试JS点击: {e}")
                self.driver.execute_script("arguments[0].click()", elem)
        else:
            logger.info(f"强制点击元素：{locator}")
            self.driver.execute_script("arguments[0].click({force: true})", elem)

    @capture_evidence
    @allure.step("____鼠标双击 - {locator}")
    def double_click(self, locator: tuple):
        """
        鼠标双击
        :param locator: 元素（定位方式，定位表达式）
        :return:
        """
        logger.info(f"鼠标双击 - {locator}")
        elem = self.driver.find_element(*locator)
        action = ActionChains(self.driver)
        action.double_click(elem).perform()

    @capture_evidence
    @allure.step("____鼠标悬停 - {locator}")
    def hover(self, locator: tuple):
        """
        鼠标悬停
        :param locator: 元素（定位方式，定位表达式）
        """
        logger.info(f"鼠标悬停 - {locator}")
        el = self.driver.find_element(*locator)
        action = ActionChains(self.driver)
        action.move_to_element(el).perform()

    @capture_evidence
    @allure.step("____输入 - {text} 元素定位 - {locator}")
    def input(self, locator: tuple, text: str) -> None:
        """
        输入内容
        :param locator: 元素（定位方式，定位表达式）
        :param text: 输入的内容
        :return: self
        """
        logger.info(f"输入 - {text} 元素定位 - {locator}")
        # 确保元素可见
        elem = self.wait_element_visible(locator)
        elem.clear()  # 清空输入框中的文本内容
        elem.send_keys(text)

    @allure.step("强制等待{seconds}秒")
    def sleep(self, seconds=1):
        """
        强制暂停
        :param seconds: 秒数 默认值为1秒
        :return: 不用返回
        """
        logger.info(f"强制等待{seconds}秒")
        time.sleep(seconds)

    @allure.step("获取当前页面路由")
    def get_current_url(self):
        """
        获取当前页面路由
        """
        url = self.driver.current_url
        logger.info(f"获取当前页面的路由：{url}")
        return url

    @allure.step("获取当前网页标题")
    def get_page_title(self):
        """
        获取网页标题
        """
        page_title = self.driver.title
        logger.info(f"获取当前页面的网页标题：{page_title}")
        return page_title

    @allure.step("____iframe切换- {reference}")
    def switch_to_frame(self, reference=None, timeout=10, poll=0.2):
        """
        iframe切换
        :param reference: 可以是id, name,索引或者元素定位（元祖）
        :param timeout:
        :param poll:
        :return:
        """
        logger.info(f"iframe切换- {reference}")
        if not reference:
            return self.driver.switch_to.default_content()
        return WebDriverWait(self.driver, timeout, poll).until(
            EC.frame_to_be_available_and_switch_to_it(reference)
        )

    @allure.step("____切换到新窗口")
    def switch_new_window(self):
        """切换到新窗口"""
        logger.info("切换到新窗口")
        # 获取所有的窗口
        windows = self.driver.window_handles
        if len(windows) >= 2:
            # 切换窗口
            self.driver.switch_to.window(self.driver.window_handles[-1])
        return self

    @allure.step("____打开一个新的窗口 - {url}")
    def new_open_window(self, url):
        """
        打开一个新窗口
        :param url: 新窗口路由
        """
        logger.info(f"打开一个新的窗口 - {url}")
        # 获取所有的窗口
        start_window = self.driver.window_handles
        # 打开新窗口
        js = 'window.open("{}")'.format(url)
        self.driver.execute_script(js)
        # 等待新窗口出现，进行切换
        WebDriverWait(self.driver, 5, 0.5).until(EC.new_window_is_opened(start_window))
        # 切换窗口
        self.driver.switch_to.window(self.driver.window_handles[-1])

    @allure.step("____获取元素 - {locator}")
    def get_element(self, locator: tuple, timeout=30):
        """
        定位元素
        :param locator:  元素定位（定位方式，定位表达式）
        :param timeout:  等待超时时间
        :return:  返回定位的元素, 如果没有找到, 则抛出异常
        """
        try:
            # Use explicit wait
            elem = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            logger.info(f"获取元素 - {locator}- 成功：{elem}")
            return elem
        except Exception as e:
            logger.error(f"根据定位：{locator} - 未找到元素 - 报错{e}")
            raise e

    @allure.step("____等待元素可见 - {locator}")
    def wait_element_visible(self, locator: tuple, timeout=30):
        """
        等待元素可见
        """
        try:
            elem = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            logger.info(f"元素可见 - {locator}")
            return elem
        except Exception as e:
            logger.error(f"等待元素可见超时：{locator} - 报错{e}")
            raise e

    @allure.step("____等待元素可点击 - {locator}")
    def wait_element_clickable(self, locator: tuple, timeout=10, poll_frequency=0.5):
        """
        等待元素可点击
        """
        try:
            elem = WebDriverWait(self.driver, timeout, poll_frequency).until(
                EC.element_to_be_clickable(locator)
            )
            logger.info(f"元素可点击 - {locator}")
            return elem
        except Exception as e:
            logger.error(f"等待元素可点击超时：{locator} - 报错{e}")
            raise e

    @allure.step("____获取所有的元素 - {locator}")
    def get_elements(self, locator):
        """
        查找元素们
        :param locator: 元素（定位方式，定位表达式）
        :return:
        """
        try:
            element_list = self.driver.find_elements(*locator)
            logger.info(f"获取所有的元素 - {locator}- 成功：{element_list}")
            return element_list
        except NoSuchElementException as e:
            logger.info(f"页面定位元素:{locator}定位失败, 错误信息：{e}")
            raise e

    @allure.step("____元素 - {locator} 可见")
    def is_element_visible(self, locator: tuple) -> bool:
        """
        断言：验证元素是否可见
        :param locator: 元素（定位方式，定位表达式）
        """
        try:
            self.driver.find_element(*locator)
            logger.info(f"元素：{locator} - 可见")
            return True
        except NoSuchElementException:
            logger.error(f"页面定位元素:{locator}不存在")
            return False

    @allure.step("____等待 - {locator} 被加载")
    def wait_element_presence(self, locator: tuple, timeout=5, poll_frequency=0.2):
        """
        显性等待： 等待元素被加载出来
        :param locator: 元素（定位方式，定位表达式）
        :return:
        """
        try:
            elem = WebDriverWait(self.driver, timeout, poll_frequency).until(
                EC.presence_of_all_elements_located(locator)
            )
            logger.info(f"等待 - {locator} 被加载：{elem}")
            return elem

        except NoSuchElementException as e:
            logger.error(f"页面定位元素:{locator}定位失败, 错误信息：{e}")
            raise e

    @allure.step("____获取元素属性值 - {locator}  - {attr_name} ")
    def get_element_attribute(self, locator: tuple, attr_name: str):
        """
        获取元素属性值
        :param locator: 元素（定位方式，定位表达式）
        :param attr_name: 元素属性名称
        :return: 元素属性值
        """
        try:
            elem = self.driver.find_element(*locator)
            res = elem.get_attribute(attr_name)
            logger.info(f"获取元素属性值 - {locator}  - {attr_name}， 值={res}")
            return res
        except Exception as e:
            logger.error(f"页面定位元素:{locator}定位失败, 错误信息：{e}")
            raise e

    @allure.step("____等待页面的请求的路径匹配 - {url}")
    def url_matches(self, url, timeout=10):
        """
        等待页面的请求的路径匹配
        :param url: 期望的url路径
        :param timeout: 超时时间 默认10s
        :return: 没有返回
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_matches(url))
            logger.info(f"页面路径:{self.driver.current_url}, 匹配路径:{url}")
        except Exception as e:
            logger.error(f"页面路径:{self.driver.current_url}, 匹配路径:{url}")
            raise e

    @allure.step("____获取元素文本值 - {locator}")
    def get_text(self, locator: tuple):
        """
        获取元素的文本值
        :param locator: 元素（定位方式，定位表达式）
        :return:
        """
        try:
            elem = self.driver.find_element(*locator)
            value = elem.text
            logger.info(f"获取元素文本值 - {locator}， 值：{value}")
            return value
        except NoSuchElementException as e:
            logger.error(f"页面定位元素:{locator}定位失败, 错误信息：{e}")
            raise e

    @allure.step("____获取所有元素文本值 - {locator}")
    def get_all_elements_text(self, locator: tuple):
        """
        获取所有元素的文本值
        :param locator: 元素（定位方式，定位表达式）
        """
        try:
            elems = self.driver.find_elements(*locator)
            res = [elem.text for elem in elems]
            logger.info(f"获取所有元素文本值  - {locator}， 值：{res}")
            return res
        except NoSuchElementException as e:
            logger.error(f"页面定位元素:{locator}定位失败, 错误信息：{e}")
            raise e

    # @allure.step("____截图 - {path}- {filename}")
    def screenshot(self, path=None, filename=None, title="点击查看截图"):
        """
         截图
        :param path: 文件保存的目录，默认为 IMG_DIR
        :param filename: 截图文件名，默认为当前时间戳
        :param title: allure报告中显示的标题
        :return:
        """
        if path is None:
            path = IMG_DIR
        if filename is None:
            filename = f"screenshot_{time.time()}.png"

        logger.info(f"截图 - {path}- {filename}")

        if not os.path.exists(path):
            os.makedirs(path)

        file_path = os.path.join(path, filename)
        self.driver.save_screenshot(file_path)
        with allure.step(f"{title} - {filename}"):
            # allure.attach.file(source=file_path, attachment_type=allure.attachment_type.PNG)
            with open(file_path, "rb") as f:
                content = f.read()
                allure.attach(
                    content, name=filename, attachment_type=allure.attachment_type.PNG
                )

    @allure.step("____执行js脚本 - {js}")
    def execute_js(self, js, *args):
        """
        执行javascript脚本
        js: 元组形式参数
        """
        try:
            self.driver.execute_script(js, *args)
            logger.info(f"执行js脚本成功:{js}")
        except Exception as e:
            logger.error(f"执行js脚本失败:{js}, 报错：{e}")
            raise e

    @allure.step("____使用selenium传文件 - 定位：{locator} - 文件：{file}")
    def upload_file_by_selenium(self, locator: tuple, file: str):
        """
        selenium直接上传文件
        要求：上传文件功能的html类型为input，例如：<input type="file" name="upload">，可以直接使用selenium中的元素定位+send_keys()方法，括号内传入文件路径
        :param locator: 元素（定位方式，定位表达式）
        :param file: 文件绝对路径, 支持传字符串
        """
        logger.info(f"使用selenium传文件 - 定位：{locator} - 文件：{file}")
        elem = self.get_element(locator)
        elem.send_keys(file)
        self.sleep()

    @allure.step("____使用pyautogui上传文件 - {file}")
    def upload_file_pyautogui(self, locator: tuple, file: str):
        """
        使用pyautogui来上传
            缺点：只能选择一个文件，路径中有中文会出问题。
            优点：跨平台。Linux, mac，windows都可以。
            安装：pip install pyautogui -i https://mirrors.aliyun.com/pypi/simple/
        :param locator: 元素（定位方式，定位表达式）
        :param file: 文件绝对路径, 支持传字符串
        """
        logger.info(f"使用pyautogui上传文件 - 定位：{locator} - 文件：{file}")
        # todo 无头模式下会上传文件不成功

        try:
            import pyautogui
        except ImportError:
            logger.error(
                "PyAutoGUI module not found. Please install it with 'pip install pyautogui'"
            )
            raise

        # 定位元素，并点击
        self.click(locator)
        # 系统之间要等待
        self.sleep(3)
        # 上传文件
        pyautogui.write(file)
        self.sleep(1)
        # 输入回车键, presses表示按的次数，按一次不会生效，有可能是执行太快，建议presses=2
        pyautogui.press("enter", 2)
        self.sleep(3)
