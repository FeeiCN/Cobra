# -*- coding: utf-8 -*-

"""
    report
    ~~~~~~~~~~~~~~~~

    Implements automation report Cobra data

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
import subprocess
import datetime
import base64
from .log import logger
from .config import Config, project_directory

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

if os.path.exists('/usr/local/bin/phantomjs'):
    phantomjs = '/usr/local/bin/phantomjs'
elif os.path.exists('/usr/bin/phantomjs'):
    phantomjs = '/usr/bin/phantomjs'
else:
    phantomjs = 'phantomjs'


class Report(object):
    def __init__(self):
        # mail
        wd = int(datetime.datetime.today().strftime("%U"))
        self.wd = wd
        self.subject = '[Cobra] 代码安全周报(W{0})'.format(wd)
        self.user = Config('email', 'username').value
        self.to = Config('report', 'to').value
        self.host = Config('email', 'host').value
        self.port = Config('email', 'port').value
        self.password = Config('email', 'password').value

        start = datetime.datetime.today() + datetime.timedelta(days=-7)
        end = datetime.datetime.today().strftime("%Y-%m-%d")
        start = start.strftime("%Y-%m-%d")
        self.param = [phantomjs, os.path.join(project_directory, 'reports', 'report.js'), project_directory, start, end]

    def run(self):
        capture = self.capture()
        if capture is False:
            logger.critical('[Capture] Capture failed')
            return False

        # send notification
        if self.notification(capture):
            return True
        else:
            logger.critical('[MAIL] Notification failed')
            return False

    def capture(self):
        """
        Use PhantomJS to capture report page
        :return: boolean
        """
        capture = None
        if os.path.exists(phantomjs) is False:
            logger.critical('[Capture] Please install phantomJS, doc: http://cobra.feei.cn/report')
            return False
        p = subprocess.Popen(self.param, stdout=subprocess.PIPE)
        result, err = p.communicate()
        if 'Critical' in result:
            logger.critical('[Capture] ' + result)
            logger.critical('[Capture] Capture exception')
            return False
        lines = result.split('\n')
        for l in lines:
            if 'reports' in l:
                capture = l.split(':')[1].strip()

        if capture is None:
            logger.critical('[Capture] get capture image file failed')
            return False
        else:
            logger.info('[Capture] The screenshot capture success: {}'.format(capture))
            return os.path.join(project_directory, capture)

    def notification(self, capture_path):
        """
        Email notification
        :param capture_path:
        :return: boolean
        """
        message = MIMEMultipart()
        message['From'] = self.user
        message['To'] = self.to
        message['Subject'] = self.subject

        # 周报图片以附件的形式发送
        # att = MIMEText(open(capture_path, 'rb').read(), 'base64', 'utf-8')
        # att['Content-Type'] = 'application/octet-stream'
        # att["Content-Disposition"] = 'attachment; filename="W({0}).png"'.format(self.wd)
        # message.attach(att)

        # 周报图片以在正文中直接显示
        with open(capture_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        text = MIMEText('<img src="data:image/png;base64,{0}">'.format(encoded_string), 'html')
        message.attach(text)

        try:
            smtp = smtplib.SMTP_SSL(host=self.host, port=self.port)
            smtp.login(self.user, self.password)
            smtp.sendmail(self.user, self.to, message.as_string())
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
            logger.critical('[EMAIL] Please config SMTP Server, port, username, to, password and sender in config file')
            return False

