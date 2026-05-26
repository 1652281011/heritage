#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/7/27 16:06 
# @Author : Scott
# @Software: PyCharm
from app.config import development
from app.config import production

config_dict = {
    'development': development,
    'production': production,
    'default': development
}
