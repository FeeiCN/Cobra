# coding=utf-8
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from .config import Config
from .log import logger


def send_mail(filename):
    host = Config("email", "host").value
    port = Config("email", "port").value
    username = Config("email", "username").value
    password = Config("email", "password").value
    sender = Config("email", "sender").value
    receiver = Config("email", "receiver").value
    is_ssl = True if Config("email", "ssl").value == "True" else False

    if is_ssl:
        server = smtplib.SMTP_SSL(host=host, port=port)
    else:
        server = smtplib.SMTP(host=host, port=port)

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = "漏洞测试报告"

    msg.attach(MIMEText("漏洞报告见附件", "plain", "utf-8"))

    with open(filename, "rb") as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attachment)

    try:
        server.login(user=username, password=password)
        server.sendmail(from_addr=sender, to_addrs=receiver, msg=msg.as_string())
        server.quit()
        logger.info("邮件推送成功")
        return True
    except smtplib.SMTPRecipientsRefused:
        logger.critical("邮件被拒收")
        return False
    except smtplib.SMTPAuthenticationError:
        logger.critical("邮件认证失败")
        return False
    except smtplib.SMTPSenderRefused:
        logger.critical("发件人被拒绝")
        return False
    except smtplib.SMTPException, error:
        logger.critical(error)
        return False
