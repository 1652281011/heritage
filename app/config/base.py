#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/7/27 16:10 
# @Author : Scott
# @Software: PyCharm
import os

from app.utils.common import get_host_ip

SECRET_KEY = os.environ.get('SECRET_KEY_PUMCH') or 'f\xf9\x05\xa9_an\xec\x5d*\x29\xd4\xc4.\x91\\N\xecO\xf4\xfaVr\xf1'
SALT_KEY = os.environ.get('SALT_KEY_PUMCH') or 'welcome to pumch 2025.'

CSRF_ENABLED = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_RECORD_QUERIES = True

# 日志文件路径
LOGFILE_PATH = os.path.join(os.getcwd(), 'logs')
# 用户的游戏数据
USER_GAME_DATA = os.path.join(os.getcwd(), 'app', 'static', 'uploads', 'user_game_data')

CURRENT_IP = get_host_ip()
PORT = 39012  # 你的端口号
FILE_BASE_URL = f'http://{CURRENT_IP}:{PORT}/static'
