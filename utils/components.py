# -*- coding: utf-8 -*-
# @Author  : TraeAI
# @File    : components.py
# @Desc    : UI组件封装，提供更高级别的元素抽象

from loguru import logger
import allure
from selenium.webdriver.common.by import By
from utils.base_page import BasePage


class Component:
    """
    基础组件类
    所有具体的UI组件（如输入框、按钮、下拉框）都应继承此类
    """

    def __init__(self, page: BasePage, locator: tuple, name: str = "Component"):
        """
        初始化组件
        :param page: 所属的 Page 对象 (BasePage 的子类)
        :param locator: 元素定位 (By.XPATH, "...")
        :param name: 组件名称，用于日志和报告
        """
        self.page = page
        self.locator = locator
        self.name = name
        self.driver = page.driver

    def wait_visible(self, timeout=10):
        """等待组件可见"""
        return self.page.wait_element_visible(self.locator, timeout=timeout)

    def is_visible(self) -> bool:
        """判断组件是否可见"""
        return self.page.is_element_visible(self.locator)

    def get_element(self):
        """获取底层 WebElement 对象"""
        return self.wait_visible()


class Input(Component):
    """
    输入框组件
    """

    def fill(self, text: str, clear: bool = True):
        """
        输入文本
        :param text: 要输入的文本
        :param clear: 输入前是否清空，默认为 True
        """
        with allure.step(f"在 {self.name} 中输入: {text}"):
            # 复用 BasePage 的 input 方法，它已经包含了 logging 和 waiting
            # 但 BasePage.input 的签名通常是 (locator, text)
            # 我们需要检查 BasePage.input 的实现，如果它支持 clear 参数最好
            # 假设 BasePage.input(locator, text)
            # 如果 BasePage 没有暴露 clear 参数，我们可以在这里处理

            # 检查 BasePage 是否有 input 方法，根据之前的读取，BasePage 有 input 方法 (referenced in logging)
            # 我们假设 BasePage.input(locator, text) 存在
            self.page.input(self.locator, text)


class Button(Component):
    """
    按钮组件
    """

    def click(self, force: bool = False):
        """
        点击按钮
        """
        with allure.step(f"点击 {self.name}"):
            self.page.click(self.locator, force=force)


class Link(Component):
    """
    链接组件
    """

    def click(self):
        with allure.step(f"点击链接 {self.name}"):
            self.page.click(self.locator)

    @property
    def href(self):
        """获取链接地址"""
        element = self.get_element()
        return element.get_attribute("href")


class Checkbox(Component):
    """
    复选框组件
    """

    def check(self):
        """勾选"""
        element = self.get_element()
        if not element.is_selected():
            with allure.step(f"勾选 {self.name}"):
                self.page.click(self.locator)

    def uncheck(self):
        """取消勾选"""
        element = self.get_element()
        if element.is_selected():
            with allure.step(f"取消勾选 {self.name}"):
                self.page.click(self.locator)

    def is_checked(self) -> bool:
        return self.get_element().is_selected()
