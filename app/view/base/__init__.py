#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/2/9 16:11 
# @Author : Scott
# @Software: PyCharm
"""基础功能"""

# 1.富文本编辑器


from flask import Blueprint

base_view = Blueprint('base_view', __name__, template_folder='templates')

from app.view.base.base import *