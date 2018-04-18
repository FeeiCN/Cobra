# coding=utf-8
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import Config
from .log import logger
from .utils import to_bool


def send_mail(target, filename, receiver):
    host = Config('email', 'host').value
    port = Config('email', 'port').value
    username = Config('email', 'username').value
    password = Config('email', 'password').value
    sender = Config('email', 'sender').value
    is_ssl = to_bool(Config('email', 'ssl').value)

    if is_ssl:
        server = smtplib.SMTP_SSL(host=host, port=port)
    else:
        server = smtplib.SMTP(host=host, port=port)

    s_sid = filename.split('.')[0]
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = '编号 {sid} 项目 Cobra 扫描报告'.format(sid=s_sid)

    msg.attach(MIMEText('扫描项目：{t}\n报告见附件'.format(t=target), 'plain', 'utf-8'))

    try:
        with open(filename, 'rb') as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.split(filename)[1])
            msg.attach(attachment)
    except IOError:
        logger.warning('[EMAIL] No such file {}, please check input parameter'.format(filename))
        return False

    try:
        server.login(user=username, password=password)
        server.sendmail(from_addr=username, to_addrs=receiver, msg=msg.as_string())
        server.quit()
        logger.info('[EMAIL] Email delivered successfully.')
        return True
    except smtplib.SMTPRecipientsRefused:
        logger.critical('[EMAIL] Email delivery rejected.')
        return False
    except smtplib.SMTPAuthenticationError:
        logger.critical('[EMAIL] SMTP authentication error.')
        return False
    except smtplib.SMTPSenderRefused:
        logger.critical('[EMAIL] SMTP sender refused.')
        return False
    except smtplib.SMTPException as error:
        logger.critical(error)
        logger.critical('[EMAIL] Please config SMTP Server, port, username, password and sender in config file')
        return False
