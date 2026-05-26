#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/7/29 09:11 
# @Author : Scott
# @Software: PyCharm

# BASE
AUTH_FAIL = 10000                                # 认证错误
CLIENT_TYPE_ERROR = 10001                        # 客户端类型错误
PARAMS_NOT_LEGAL = 10010                         # 参数不正确
DATABASE_TABLE_INSERT_ERROR = 10031              # 数据表插入失败
FILE_TOO_BIG = 10041                             # 文件太大
FILE_TYPE_NOT_ALLOWED = 10042                    # 文件类型不被允许
MOBILE_TYPE_ERROR = 10043                        # 手机格式不正确
FILE_UPLOAD_ERROR = 10044                        # 文件上传失败
ID_CARD_TYPE_ERROR = 10045                       # 身份证号格式错误
DATA_NOT_EXISTS = 10050                          # 数据不存在
DATA_EXISTS = 10051                              # 数据已存在
RESOURCE_NOT_FOUND=10052                        #资源未发现
DATABASE_TABLE_UPDATE_ERROR=10053               #插入数据库错误

# API
API_TEMPORARY_NOT_USABLE = 10030                 # API不可用

# 表示用户需要重新登录的几种状态--返回给客户端错误码统一为20004,具体错误要参照错误描述
USER_NOT_ACTIVE_OR_LOCKED = 20003                # 用户没有激活或被锁定
AUTH_TOKEN_ERROR = 20004                         # auth-token无效、错误或者不存在
AUTH_TOKEN_OVERDUE = 20009                       # auth-token过期
CURRENT_USER_ID_ERROR = 20005                    # 传入的current-user-id与auth-token获得用户的id不同
THIRD_PARTY_LOGIN_FAILED = 20016                 # 第三方登录失败

# user auth
USER_NOT_EXISTS = 20001                          # 用户不存在
USER_PASSWORD_NOT_CORRECT = 20002                # 密码不正确
USER_IS_EXISTS = 20006                           # 用户已经存在 重复注册
USER_HAS_NO_PERMISSION = 20007                   # 当前用户没有权限
USER_HAS_NO_LOG_OFF = 20014                      # 当前用户有未完成订单，不可注销
USER_IDENTITY_ERROR = 20015                      # 当前用户身份不正确，不可进行该操作

SYSTEM_ERROR = 40001
POST_NOT_EXISTS = 404