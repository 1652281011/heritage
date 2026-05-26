#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2023/2/13 11:44 
# @Author : Scott
# @Software: PyCharm
"""微信小程序"""

import json
from app.utils.common import urllib_get
from app.utils.tencent.common.WXBizDataCrypt import WXBizDataCrypt

class WeChatApplet(object):

    def __init__(self, app_id, app_secret):
        self.__appid = app_id
        self.__app_secret = app_secret

    def auth_code2Session(self, code):
        # 登录
        # 文档url：https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
        auth_url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'.format(
            self.__appid, self.__app_secret, code)

        res = urllib_get(url=auth_url)
        if not res:
            return False
        res_json = json.loads(
            res)  # {u'openid': u'oAZTb5EdAJkWn_vTGOulXVp1vo-M', u'session_key': u'NSozttV9PRfzdGeM6qLUlw==', u'unionid': u'ojqvLv9CPrLhcfKm6eGZJNfUS-0E'}

        # 判断是否请求成功
        if 'errcode' in res_json.keys() and res_json['errcode'] != 0:
            return False

        return res_json

    # 解密手机号
    def decrypt_mobile(self, encryptedData, iv, session_key):
        wx_crypt = WXBizDataCrypt(self.__appid, session_key)
        # decrypt = wx_crypt.decrypt(encryptedData, iv)
        # mobile = mobile_dict['phoneNumber']

        return wx_crypt.decrypt(encryptedData, iv)
