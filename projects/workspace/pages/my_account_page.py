# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : my_account_page.py
# @Desc    :

from selenium.webdriver.common.by import By
from utils.base_page import BasePage
import allure


class MyAccountPage(BasePage):
    """
    我的账号页面
    """

    # ==========================
    # 页面元素定位配置
    # 已优化：使用相对路径和属性定位，替代不稳定的绝对路径
    # ==========================

    # 真实姓名输入框 - 假设有 placeholder 或 label
    # 如果没有 placeholder，可以尝试定位 label 的兄弟元素
    # 暂时使用更稳健的相对 XPath，寻找 form 下的 input
    _REAL_NAME_INPUT = (
        By.XPATH,
        "//form//input[@placeholder='请输入真实姓名' or contains(@placeholder, '姓名')]",
    )

    # 手机号输入框
    _PHONE_INPUT = (
        By.XPATH,
        "//form//input[@placeholder='请输入手机号' or contains(@placeholder, '手机')]",
    )

    # 邮箱输入框
    _EMAIL_INPUT = (
        By.XPATH,
        "//form//input[@placeholder='请输入邮箱' or contains(@placeholder, '邮箱')]",
    )

    # 更新/保存按钮
    _UPDATE_BUTTON = (
        By.XPATH,
        "//form//button[contains(., '保存') or contains(., '更新')]",
    )

    @allure.step("在个人中心更新信息：姓名-{name}, 手机-{phone}, 邮箱-{email}")
    def update_basic_info(self, name, phone, email):
        """
        功能：填写并提交个人基本信息
        :param name: 真实姓名
        :param phone: 手机号码
        :param email: 电子邮箱
        """
        # 1. 确保姓名输入框可见，说明页面加载好了
        self.wait_element_visible(self._REAL_NAME_INPUT)

        # 2. 输入信息
        self.input(self._REAL_NAME_INPUT, name)
        self.input(self._PHONE_INPUT, phone)
        self.input(self._EMAIL_INPUT, email)

        # 3. 点击更新按钮
        self.wait_element_clickable(self._UPDATE_BUTTON)
        self.click(self._UPDATE_BUTTON)
