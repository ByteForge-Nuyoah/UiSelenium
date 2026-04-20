# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : login_page.py
# @Desc    : 登录页面的元素定位 和 操作

import allure
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from utils.base_page import BasePage
from utils.api.request_control import url_handle
from utils.components import Input, Button


class LoginPage(BasePage):
    # 页面元素定位
    # 使用 placeholder 属性定位，比绝对路径更稳定，且不受动态ID影响
    # 用户提供的绝对路径参考：/html/body/div[1]/div/div/div[2]/div[2]/div/form/div[1]/div/div/div/input
    _USERNAME_INPUT = (By.XPATH, "//input[@placeholder='请输入账号']")
    _PASSWORD_INPUT = (By.XPATH, "//input[@placeholder='请输入密码']")

    # 登录按钮，通常包含"登录"文字
    _LOGIN_BUTTON = (By.XPATH, "//button[contains(., '登录')]")

    # 登录成功后的元素
    # 建议使用更明确的元素，如用户头像、退出按钮等
    # 这里结合URL判断和通用元素判断
    _LOGIN_SUCCESS_ELEMENT = (
        By.XPATH,
        "//div[contains(@class, 'avatar') or contains(text(), '退出') or contains(text(), 'User')]",
    )

    def __init__(self, driver):
        super().__init__(driver)
        # 初始化组件
        self.username_input = Input(self, self._USERNAME_INPUT, "用户名输入框")
        self.password_input = Input(self, self._PASSWORD_INPUT, "密码输入框")
        self.login_button = Button(self, self._LOGIN_BUTTON, "登录按钮")

    def open_site(self, host, clear_session=True):
        """
        打开登录页面
        :param host: 基础域名地址
        :param clear_session: 是否清理已登录状态，默认清理
        """
        full_url = url_handle(host, "/login")
        
        if clear_session:
            with allure.step(f"访问登录页面：{host}/login"):
                self.visit(full_url)

                is_logged_in = False
                try:
                    if self.is_element_visible(self._LOGIN_SUCCESS_ELEMENT):
                        is_logged_in = True
                except Exception:
                    pass

                if not is_logged_in and "/login" not in self.driver.current_url:
                    is_logged_in = True

                if is_logged_in:
                    with allure.step("检测到已登录状态，执行清理环境操作"):
                        self.driver.execute_script("window.localStorage.clear();")
                        self.driver.execute_script("window.sessionStorage.clear();")
                        self.driver.delete_all_cookies()
                        self.visit(full_url)
                        self.driver.refresh()

                self.wait_element_visible(self._USERNAME_INPUT)
        else:
            with allure.step("复用已登录session，跳过登录页面清理"):
                logger.info("复用session模式，不清理登录状态")
                if "/login" in self.driver.current_url:
                    logger.warning("当前仍在登录页，session可能已失效")
                    self.wait_element_visible(self._USERNAME_INPUT)
                else:
                    logger.info("已登录状态验证成功，跳过登录步骤")

    def input_username(self, username):
        """
        输入用户名
        :param username: 用户账号
        """
        with allure.step(f"输入用户名：{username}"):
            self.input(self._USERNAME_INPUT, text=username)

    def input_password(self, password):
        """
        输入密码
        :param password: 用户密码
        """
        with allure.step(f"输入密码：{password}"):
            self.input(self._PASSWORD_INPUT, text=password)

    def click_login_button(self):
        """
        点击登录按钮
        """
        with allure.step("点击登录按钮"):
            self.click(self._LOGIN_BUTTON)

    def login(self, username, password):
        """
        执行完整的登录流程
        :param username: 用户账号
        :param password: 用户密码
        """
        self.input_username(username)
        self.input_password(password)
        self.click_login_button()

    def is_login_success(self, timeout=10):
        """
        判断是否登录成功
        逻辑：
        1. 检查URL是否不包含 'login' (带等待)
        2. 或者检查是否存在登录后的特定元素
        """
        logger.info(f"开始检查登录状态，超时时间: {timeout}")
        with allure.step("检查是否登录成功"):
            try:
                # 方法1：等待URL变化 (最快且最准确)
                # 等待直到URL中不包含'/login'
                logger.info(f"当前URL: {self.driver.current_url}")
                WebDriverWait(self.driver, timeout).until(
                    lambda d: "/login" not in d.current_url
                )
                logger.info("URL检查通过，登录成功")
                return True
            except Exception as e:
                logger.warning(f"URL检查超时或失败: {e}")
                # 如果URL等待超时，尝试最后检查一次元素
                # 注意：这里可能需要根据实际页面调整 _LOGIN_SUCCESS_ELEMENT
                try:
                    return self.is_element_visible(
                        self._LOGIN_SUCCESS_ELEMENT, timeout=2
                    )
                except:
                    return False
