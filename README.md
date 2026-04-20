# UI Automation Framework (Web UI 自动化测试框架)

基于 **Python 3 + Pytest + Selenium 4 + Allure + Loguru** 的现代化 Web UI 自动化测试框架。本框架致力于提供稳定、高效、易扩展且**支持多项目复用**的自动化测试解决方案。

## ✨ 核心特性

*   **多项目支持**：一套框架管理多个业务项目，配置隔离，独立运行，最大化复用基础设施。
*   **极简架构设计**：扁平化的工具类库结构，拒绝过度封装，让代码触手可及，易于阅读和二次开发。
*   **PageObject 设计模式**：页面元素与测试逻辑分离，提高代码可维护性。
*   **Session 复用**：已登录状态下自动复用 session，跳过重复登录，显著提升多用例运行效率。
*   **智能定时任务**：内置定时任务调度器，支持通过配置文件定义每日执行时间（如每天 22:00）。
*   **动态元素定位**：针对动态 ID 元素，采用相对路径和属性定位，确保脚本稳健运行。
*   **自动截图与分类**：
    *   **成功截图**：可配置开启，自动归档至 `outputs/image/success/<browser>/`。
    *   **失败截图**：自动归档至 `outputs/image/fail/<browser>/`，并自动附加到 Allure 报告中。
*   **多环境支持**：一键切换测试环境（Test）、预发布环境（Pre）和生产环境（Live）。
*   **数据驱动**：支持 YAML 数据文件，实现数据与代码分离，方便非技术人员维护。
*   **多渠道通知**：集成 **钉钉**、**企业微信**、**飞书** 和 **邮件** 通知，测试结果即时触达。
*   **Docker & CI/CD**：内置 Dockerfile，提供 GitHub Actions 完整流水线配置。

## 📂 目录结构

```text
UiSelenium/
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI 配置
├── config/                  # 全局配置文件 (默认配置)
│   └── default_config.yaml  # 默认运行配置
├── local_drivers/           # 本地浏览器驱动 (chromedriver/msedgedriver等)
├── projects/                # 多项目目录 (核心业务代码)
│   ├── workspace/           # 示例项目
│   │   ├── config/          # 项目级配置 (覆盖全局配置)
│   │   ├── data/            # 测试数据 (YAML)
│   │   ├── pages/           # 页面对象 (PO模式)
│   │   └── testcases/       # 测试用例 (Pytest)
│   └── new_project/         # 新项目 (结构同上)
├── utils/                   # 通用工具类库
├── outputs/                 # 测试产出物 (报告/日志/截图)
├── run.py                   # 框架统一启动入口
├── requirements.txt         # 依赖清单
├── Dockerfile               # 容器构建文件
└── pytest.ini               # Pytest 核心配置
```

## 🚀 快速开始 (Quick Start)

### 1. 环境准备

*   Python 3.9+
*   Chrome 浏览器 (推荐)
*   Web Driver: 将对应版本的 `chromedriver` 或 `msedgedriver` 放入 `local_drivers/` 目录。

### 2. 安装依赖

```bash
# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 运行测试

```bash
# 运行默认项目 (workspace) 在 test 环境
python run.py

# 运行指定项目
python run.py -project workspace

# 指定环境和浏览器
python run.py -env test -driver_type chrome-headless

# 开启 Allure 报告生成
python run.py -report yes -open no

# 开启定时任务模式
python run.py -schedule yes
```

### 4. 运行参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-env` | 运行环境 (test, live) | test |
| `-driver_type` | 浏览器类型 (chrome, chrome-headless, firefox, edge) | chrome |
| `-report` | 是否生成 Allure 报告 (yes, no) | yes |
| `-open` | 是否自动打开报告 (yes, no) | yes |
| `-project` | 指定运行的项目名称 | workspace |
| `-schedule` | 开启定时任务模式 (yes, no) | no |

## 📝 开发示例 (Example)

本框架遵循 **PageObject** 设计模式和 **数据驱动** 思想。以下是一个标准的开发流程示例。

### 1. 定义测试数据 (YAML)
在 `projects/<project_name>/data/` 下创建数据文件，例如 `login_case_data.yaml`：

```yaml
case_common:
  allure_epic: "workspace"
  allure_feature: "登录模块"

login_page_success:
  allure_story: "登录"
  cases:
    - title: "网页登录: 正确用户名和密码登录成功"
      run: true                  # 控制用例是否执行
      severity: normal           # 用例等级 (blocker, critical, normal, minor, trivial)
      login_user: "${username}"  # 登录账号 (用于 login_driver fixture)
      login_password: "${password}" # 登录密码 (用于 login_driver fixture)
      user: "${username}"        # 支持引用全局变量
      password: "${password}"
```

### 2. 封装页面对象 (Page Object)
在 `projects/<project_name>/pages/` 下创建页面类，例如 `login_page.py`：

```python
from selenium.webdriver.common.by import By
from utils.base_page import BasePage
import allure

class LoginPage(BasePage):
    _USERNAME_INPUT = (By.XPATH, "//input[@placeholder='请输入账号']")
    _PASSWORD_INPUT = (By.XPATH, "//input[@placeholder='请输入密码']")
    _LOGIN_BUTTON = (By.XPATH, "//button[contains(., '登录')]")

    def open_site(self, host, clear_session=True):
        """
        打开登录页面
        :param host: 基础域名地址
        :param clear_session: 是否清理已登录状态，默认清理
        """
        full_url = f"{host}/login"
        with allure.step(f"访问登录页面：{full_url}"):
            self.visit(full_url)
            if clear_session:
                # 清理已登录状态
                self.driver.execute_script("window.localStorage.clear();")
                self.driver.execute_script("window.sessionStorage.clear();")
                self.driver.delete_all_cookies()
                self.visit(full_url)
            self.wait_element_visible(self._USERNAME_INPUT)

    def login(self, username, password):
        with allure.step(f"登录操作：{username}"):
            self.input(self._USERNAME_INPUT, username)
            self.input(self._PASSWORD_INPUT, password)
            self.click(self._LOGIN_BUTTON)
```

### 3. 编写测试用例 (Test Case)
在 `projects/<project_name>/testcases/` 下创建测试文件，例如 `test_login.py`：

```python
import pytest
import allure
from utils.data.yaml_handle import get_yaml_data
from utils.data.data_handle import data_handle
from config.global_vars import GLOBAL_VARS
from projects.workspace.pages.login_page import LoginPage

# 加载数据
data = get_yaml_data("login_case_data.yaml", __file__)

@allure.epic(data["case_common"]["allure_epic"])
@allure.feature(data["case_common"]["allure_feature"])
class TestLogin:
    
    @allure.story(data["login_page_success"]["allure_story"])
    @pytest.mark.parametrize(
        "case", 
        data["login_page_success"]["cases"],
        ids=[case["title"] for case in data["login_page_success"]["cases"]]
    )
    def test_login_success(self, case, login_driver):
        """
        login_driver fixture 已自动完成登录，此处验证登录状态
        """
        case_data = data_handle(case, GLOBAL_VARS)
        driver = login_driver
        login_page = LoginPage(driver)
        
        assert login_page.is_login_success(), "登录失败"
```

### 4. 配置 Fixture (Session 复用)
在 `projects/<project_name>/testcases/conftest.py` 中配置 `login_driver` fixture：

```python
_logged_in = False

@pytest.fixture(scope="function")
def login_driver(init_driver, case):
    """
    登录Fixture：执行登录操作并返回driver
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
                _logged_in = True
    else:
        with allure.step("前置步骤：复用已登录session"):
            login_page.open_site(host, clear_session=False)

    yield driver
```

## ⚙️ 配置说明

### 运行配置 (default_config.yaml)

```yaml
run:
  # 是否生成allure html report
  report: "yes"
  
  # 是否自动打开allure html report
  open: "yes"
  
  # 运行环境: test, live
  env: "test"
  
  # 浏览器驱动类型
  driver_type: "chrome"
  
  # 成功截图: true 开启, false 关闭（仅失败时截图）
  success_screenshot: false
```

### 多项目配置

在项目目录下创建 `config/project_config.yaml`，该文件优先级高于全局配置：

```yaml
# projects/shop_app/config/project_config.yaml
project_name: "电商平台自动化测试"

# 通知配置 (覆盖全局)
notification:
  ding_talk:
    token: "your_dingtalk_token"

# 定时任务 (覆盖全局)
cron:
  enabled: true
  time: "20:00"
```

## ⏰ 定时任务 (Auto Run)

框架内置了轻量级定时任务调度器。

### 配置
在 `env_config.yaml` 或项目级 `project_config.yaml` 中配置：

```yaml
cron:
  enabled: true
  time: "22:00"  # 每天晚上 10 点执行
```

### 启动
使用 `-schedule yes` 参数启动框架，它将进入守护进程模式，并在指定时间自动触发测试。

```bash
nohup python run.py -schedule yes > cron.log 2>&1 &
```

## 🔄 GitHub Actions CI/CD

框架内置 GitHub Actions 流水线配置，支持自动测试和通知。

### 触发条件
- Push 到 master/main/develop 分支
- Pull Request 到 master/main 分支
- 手动触发 (workflow_dispatch)

### 运行命令

```bash
# 本地测试
python run.py -env test -driver_type chrome-headless -report yes -open no -project workspace
```

### 通知配置
在 GitHub 仓库的 Settings → Secrets 中添加：
- `DINGTALK_WEBHOOK`: 钉钉机器人 webhook URL

### Artifacts
- `allure-report`: Allure 测试报告 (保留 7 天)
- `screenshots`: 失败截图 (仅失败时上传)

## 🐳 Docker 运行

### 构建镜像

```bash
docker build -t ui-auto .
```

### 运行容器

```bash
# 默认运行
docker run --rm -v $(pwd)/outputs:/app/outputs ui-auto

# 指定环境和项目
docker run --rm \
  -e ENV=test \
  -e PROJECT=workspace \
  -v $(pwd)/outputs:/app/outputs \
  ui-auto
```

### 2. 依赖管理
新增第三方库后，请更新 `requirements.txt`：
```bash
pip freeze > requirements.txt
```

### 3. Session 复用机制
- 使用 `login_driver` fixture 的测试用例会自动复用 session
- 测试数据需包含 `login_user` 和 `login_password` 字段
- 首次登录后 `_logged_in=True`，后续用例跳过登录步骤

### 4. 截图配置
- `success_screenshot: true` - 每条用例成功时截图
- `success_screenshot: false` - 仅失败时截图（节省存储空间）
