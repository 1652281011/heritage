#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/7/27 16:15 
# @Author : Scott
# @Software: PyCharm

from app.view.error import error_view
from app.view.base import base_view

blueprints = [
    (error_view, ''),
    (base_view, '')
]
