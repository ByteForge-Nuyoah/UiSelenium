# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : yaml_handle.py
# @Desc    : YAML文件读取封装

import os
import yaml
from loguru import logger
from config.path_config import DATA_DIR, PROJECTS_DIR
from config.global_vars import GLOBAL_VARS


def get_yaml_data(file_name, current_path=None):
    """
    读取YAML文件内容
    :param file_name: 文件名 (包含后缀, 如 login_case_data.yaml)
    :param current_path: 当前调用文件的路径 (建议传 __file__)，用于自动推断项目路径
    :return: 字典或列表数据
    """
    file_path = None

    # 1. 尝试从 current_path 推断项目路径
    if current_path:
        # 统一路径分隔符
        abs_path = os.path.abspath(current_path)
        parts = abs_path.split(os.sep)

        # 查找 'projects' 目录的位置
        if "projects" in parts:
            try:
                # 获取 projects 的索引
                idx = parts.index("projects")
                # 项目名称应该是 projects 的下一级
                if idx + 1 < len(parts):
                    project_name = parts[idx + 1]
                    # 构造该项目的 data 目录路径
                    # .../projects/workspace/data/file_name
                    # 我们需要找到 projects 目录的父级路径
                    base_parts = parts[: idx + 2]  # 到项目名为止
                    project_root = os.sep.join(base_parts)
                    candidate_path = os.path.join(project_root, "data", file_name)

                    if os.path.exists(candidate_path):
                        file_path = candidate_path
                        logger.debug(f"根据路径推断找到数据文件: {file_path}")
            except Exception as e:
                logger.warning(f"从路径推断项目失败: {e}")

    # 2. 如果推断失败，检查是否指定了全局项目
    if not file_path:
        project_name = GLOBAL_VARS.get("project_name")
        if project_name:
            candidate_path = os.path.join(PROJECTS_DIR, project_name, "data", file_name)
            if os.path.exists(candidate_path):
                file_path = candidate_path
            else:
                # 如果项目目录下没有，尝试去公共data目录找
                logger.warning(
                    f"项目 {project_name} 下未找到 {file_name}，尝试从公共目录读取"
                )

    # 3. 最后尝试公共 data 目录
    if not file_path:
        file_path = os.path.join(DATA_DIR, file_name)

    if not os.path.exists(file_path):
        logger.error(f"YAML文件不存在: {file_path}")
        raise FileNotFoundError(f"YAML文件不存在: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        logger.error(f"读取YAML文件失败: {file_path}, 错误: {e}")
        raise e


class YamlHandle:
    """
    YAML文件操作类 (保留兼容性)
    """

    def __init__(self, filename):
        """
        初始化用例文件
        :param filename: 文件绝对路径
        """
        self.filename = filename

    @property
    def read_yaml(self):
        try:
            with open(file=self.filename, mode="r", encoding="utf-8") as fp:
                return yaml.safe_load(fp.read())
        except FileNotFoundError as e:
            logger.error(f"YAML file ({self.filename}) not found: {e}")
            raise e
        except yaml.YAMLError as e:
            logger.error(f"Error while reading YAML file ({self.filename}): {e}")
            raise e

    def write(self, data, mode="a"):
        """
        往yaml文件中写入数据，默认是追加写入
        :param data: 要写入的数据
        :param mode: 写入模式
        :return:
        """
        try:
            with open(self.filename, mode=mode, encoding="utf-8") as f:
                yaml.dump(data, f)
        except yaml.YAMLError as e:
            logger.error(f"Error while writing to YAML file ({self.filename}): {e}")
            raise e
