#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/7/27 16:01
# @Author : Scott
# @Software: PyCharm
import os
from app import create_app, socketio
from flask_socketio import SocketIO
import logging
from flask_cors import CORS
config_name = (os.getenv('FLASK_CONFIG') or 'default')
app = create_app(config_name=config_name)
app.logger.setLevel(logging.INFO)
CORS(app)  # 跨域请求

app.logger.info("------boot manage--------")
if __name__ == '__main__':
    # socketio.run(app)  # 使用 SocketIO 的 run 方法启动应用

    app.run()
