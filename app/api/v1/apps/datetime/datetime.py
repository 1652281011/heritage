#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : renxp
# @Time     : 2024/12/13 13:12
# @File     : datetime.py
# @Project  : psy-admin

from flask_restful import Resource

from datetime import datetime,date,time,timedelta
from flask import current_app, g, request, jsonify
from app.api.common.fields import test_fields
from app.api.common.parser import test_parser
from app.api.common.response import success
class DateTime(Resource):

    def get(self):
        datetime_t=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = {
            "resid": 200,
            "msg": "请求成功",
            "status": "success",
            "data": {

                'datetime': datetime_t
            }
        }

        return jsonify(res)