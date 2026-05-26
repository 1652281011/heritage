#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/29 上午12:13
# @Software：PyCharm
# @Author  : scott
from flask import Blueprint

error_view = Blueprint('error_view', __name__, template_folder='templates')

from app.view.error.error import *