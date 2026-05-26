#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/29 上午12:13
# @Software：PyCharm
# @Author  : scott
import json
import os

from flask import request, g

from app.api.common.response import error
from app.view.error import error_view


# 请求之前的钩子
@error_view.before_app_request
def before_request():
    if os.getenv('FLASK_CONFIG') != 'production' and request.method != 'GET':
        print('----Request Header---- %s' % request.path)
        for x, y in request.headers.items():
            print('%s=%s' % (x, y))
        if request.headers.get('content-type') == 'application/json':
            print('----Request Body---- %s' % request.path)
            print(json.dumps(request.json, ensure_ascii=False, indent=4))
    # 经度
    g.lat = request.headers.get('lat', 0)
    # 维度
    g.lng = request.headers.get('lng', 0)
    # 这个是APP传递过来的SN，可用于手动生成auth_token，可保存登录日志
    g.sn = request.headers.get('sn')
    # app类型,默认设为w-applet. (web, ios, android, weixin, w-applet(微信小程序), w-applet-1(微信小程序2))
    g.app_type = request.headers.get('app-type', 'w-applet')
    # api类型。默认app。 admin后台管理系统
    g.api_type = request.headers.get('api-type', 'app')
    # 版本号，APP端传递
    g.version = request.headers.get('version', '')
    # 当前请求的用户id，要求登录后请求的接口必传.通过对比验证
    g.current_user_id = request.headers.get('current-user-id', '')
    # 前段静态文件版本后缀
    g.v = '1.1.3'
    # 登录认证auth_token
    g.auth_token = request.headers.get('auth-token')
    # 用户登录状态信息
    g.user_login_data = ''


# 请求之后的钩子
@error_view.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
    allow_headers = "Referer, Accept, Origin, User-Agent, X-Requested-With, X_Requested_With, Content-Type, App-Type, Api-Type, Sn, Sessionid, Auth-Token, Current-User-Id, User-Id"
    response.headers['Access-Control-Allow-Headers'] = allow_headers
    response.headers['Access-Control-Allow-Credentials'] = True
    response.header = "Content-Security-Policy: upgrade-insecure-requests"
    if os.getenv('FLASK_CONFIG') != 'production' and response.content_type == 'application/json':
        print('\n----------Response Data------------')
        print(response.headers)
        print(response.data)
        print('----------End Response Data------------\n')
    return response


@error_view.app_errorhandler(403)
def forbidden(e):
    # res = request.headers.get('Content-Type')
    # if res == 'application/json':
    return error(msg=u'访问被拒绝了', resid=403)
    # return render_template('error/403.html'), 403


@error_view.app_errorhandler(404)
def page_not_found(e):
    # res = request.headers.get('Content-Type')
    # if res == 'application/json':
    return error(msg=u'不存在的访问请求')
    # return render_template('error/404.html'), 404


@error_view.app_errorhandler(500)
def internal_server_error(e):
    # res = request.headers.get('Content-Type')
    # if res == 'application/json':
    return error(msg=u'服务器错误', resid=500)
    # return render_template('error/500.html'), 500

# @error_view.app_errorhandler(InvalidAPIUsage)
# def handle_invalid_usage(errors):
#     response = jsonify(errors.to_dict())
#     response.status_code = errors.status_code
#     return response
