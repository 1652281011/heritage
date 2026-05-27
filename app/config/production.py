#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/7/27 16:07 
# @Author : Scott
# @Software: PyCharm

from app.config.base import *

# LOG_LEVEL = 'WARNING'

LOG_LEVEL = 'INFO'

SQLALCHEMY_DATABASE_URI = os.environ.get(
    'SQLALCHEMY_DATABASE_URI_XINLS') or 'mysql+pymysql://heritage_admin:123456@127.0.0.1:3306/heritage'

# redis的配置
# 服务器
REDIS_URL = os.environ.get('REDIS_URL_MUSICAL_COPYRIGHT') or 'redis://:123456@127.0.0.1:6379/0'
# 本地
# REDIS_URL = os.environ.get('REDIS_URL_MUSICAL_COPYRIGHT') or 'redis://:@127.0.0.1:6379/6'


# APScheduler 配置（使用默认的内存 JobStore）
SCHEDULER_API_ENABLED = True
# config.py 或相应配置文件
SCHEDULER_EXECUTE_IN_APP_CONTEXT = True

SCHEDULER_EXECUTORS = {
    'default': {
        'type': 'threadpool',
        'max_workers': 10
    }
}
SCHEDULER_JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3
}