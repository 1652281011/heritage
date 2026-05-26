#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/27 下午10:45
# @Software：PyCharm
# @Author  : scott
import datetime
import time
from app.models import db
from sqlalchemy import func


class BaseModel:
    # # 注册时间
    # c_time = db.Column(db.DateTime, server_default=func.now())
    # # 更新时间
    # e_time = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))
    e_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))