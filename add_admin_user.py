#!/usr/bin/env python2
import time
from app import db, CobraAdminUser

# Change your username and password here
username = 'admin'
password = 'admin123456'
role = 1    # 1: super admin, 2: admin, 3: rules admin


# Do not edit these code below this line #
##########################################
current_time = time.strftime('%Y-%m-%d %X', time.localtime())
au = CobraAdminUser(username, password, role, None, None, current_time, current_time)
if password == "admin123456" or password == "123456" or password == "admin" or \
   password == "12345" or password == "root" or password == "toor" or password == "admin888":
    print '[*] WARNING: Weak password detected! You\'d better choose a strong password.'
if len(password) < 6:
    print '[*] DANGER: Password length must be over 6 characters!'
    exit(1)
try:
    db.session.add(au)
    db.session.commit()
    print '[*] add user ' + username + ' success!'
except Exception, e:
    print e.message
    print '[*] add failed.'

