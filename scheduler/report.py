# -*- coding: utf-8 -*-

"""
    scheduler.report
    ~~~~~~~~~~~~~~~~

    Implements automation report Cobra data

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import subprocess
import logging
import base64
import datetime
from utils import log
from utils.config import Config

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

log.Log()
logging = logging.getLogger(__name__)

phantomjs = '/usr/local/bin/phantomjs'
time_types = ['w', 'm', 'q']
time_type_des = {
    'w': '周',
    'm': '月',
    'q': '季'
}


class Report(object):
    def __init__(self, time_type):
        if time_type not in time_types:
            logging.critical('Time type exception')
            return

        self.time_type_de = time_type_des[time_type]

        # mail
        wd = int(datetime.datetime.today().strftime("%U"))
        self.subject = '[Cobra] 代码安全{0}报(W{1})'.format(self.time_type_de, wd)
        self.user = Config('email', 'user').value
        self.name = Config('email', 'name').value
        self.to = Config('report', 'to').value
        self.host = Config('email', 'host').value
        self.port = Config('email', 'port').value
        self.password = Config('email', 'password').value

        self.param = [phantomjs, os.path.join(Config().project_directory, 'scheduler', 'report.js'), Config().project_directory, time_type]

    def run(self):
        capture = self.capture()
        if capture is False:
            logging.critical('Capture failed')
            return False

        # send notification
        if self.notification(capture):
            return True
        else:
            logging.critical('Notification failed')
            return False

    def capture(self):
        """
        Use PhantomJS to capture report page
        :return: boolean
        """
        capture = None
        p = subprocess.Popen(self.param, stdout=subprocess.PIPE)
        result, err = p.communicate()
        if 'Critical' in result:
            logging.critical('Capture exception')
            return False
        lines = result.split('\n')
        for l in lines:
            if 'reports' in l:
                capture = l.split(':')[1].strip()

        if capture is None:
            logging.critical('get capture image file failed')
            return False
        else:
            return os.path.join(Config().project_directory, capture)

    def notification(self, capture_path):
        """
        Email notification
        :param capture_path:
        :return: boolean
        """
        msg = MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = '{0}<{1}>'.format(self.name, self.user)
        msg['To'] = self.to

        with open(capture_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        text = MIMEText('<img src="data:image/png;base64,{0}">'.format(encoded_string), 'html')
        msg.attach(text)

        s = smtplib.SMTP(self.host, self.port)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self.user, self.password)
        s.sendmail(self.user, self.to, msg.as_string())
        s.quit()
        return True
