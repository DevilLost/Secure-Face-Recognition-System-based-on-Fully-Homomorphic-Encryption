# -*- coding: utf-8 -*-
# @author: Toby

import os
from datetime import timedelta

# APP
DEBUG = False
MAX_CONTENT_LENGTH = 6 * 1024 * 1024
SECRET_KEY = os.urandom(24)
PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=5)

# Flask-WTF
WTF_CSRF_TIME_LIMIT = 7200

# 数据库(MySQL5.7)
DIALECT = 'mysql'
DRIVER = 'mysqldb'
# 数据库用户名
USERNAME = 'root'
# 数据库密码
PASSWORD = '123456'
# 数据库地址(默认本地)
HOST = '127.0.0.1'
# 数据库端口(默认端口)
PORT = '3306'
# 数据库库名
DATABASE = 'face'

SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(
    DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = False
