# -*- coding: utf-8 -*-
# @Author  : 会飞的🐟
# @File    : yagmail_bot.py
# @Desc    : 通过第三方模块yagmail发送邮件

# 标准库导入
import os

# 第三方库导入
from loguru import logger
import yagmail


class YagEmailServe:
    def __init__(self, host, user, password):
        """
        user(发件人邮箱), password(邮箱授权码), host(发件人使用的邮箱服务 例如：smtp.163.com)
        """
        self.host = host
        self.user = user
        self.password = password

    def send_email(self, info: dict):
        """
        发送邮件
        :param info:包括,contents(内容), to(收件人列表), subject(邮件标题), attachments(附件列表)
        info = {
            "subject": "",
            "contents": "",
            "to": "",
            "files": ""
        }
        :return:
        """
        try:
            logger.debug(f"准备发送邮件: To={info['to']}, Subject={info['subject']}")
            yag = yagmail.SMTP(user=self.user, password=self.password, host=self.host)
            # 如果存在附件，则与邮件内容一起发送附件，否则仅发送邮件内容
            if info.get("attachments") and os.path.exists(info["attachments"]):
                yag.send(
                    to=info["to"],
                    subject=info["subject"],
                    contents=info["contents"],
                    attachments=info["attachments"],
                )
            else:
                if info.get("attachments"):
                    logger.warning(f"邮件附件不存在: {info['attachments']}, 仅发送内容")
                yag.send(
                    to=info["to"], subject=info["subject"], contents=info["contents"]
                )
            yag.close()
            logger.info(f"邮件发送成功: To={info['to']}")
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
