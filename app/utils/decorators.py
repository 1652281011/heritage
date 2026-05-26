#!/usr/bin/env python
# -*- coding: utf-8 -*-
from functools import wraps
from flask import g, request
from app.api.common.error_code import AUTH_TOKEN_ERROR, USER_HAS_NO_PERMISSION, USER_NOT_ACTIVE_OR_LOCKED
from app.api.common.response import error
from app.models.DoctorInfo import DoctorInfo
from app.models.users import User
from app.services.adminlog.adminlog_service import AdminLogService

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.auth_token:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请登录后操作')
        if g.api_type == 'admin':
            admin = DoctorInfo.verify_auth_token(g.auth_token)
            if not admin:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')
            if admin.delete is True:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户已经被禁用或冻结'.format(USER_NOT_ACTIVE_OR_LOCKED))
            g.admin = admin
        else:
            user = User.verify_auth_token(g.auth_token, g.app_type)
            if not user:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')
            if hasattr(user, 'status') and user.status == 0:
                return error(resid=AUTH_TOKEN_ERROR, msg=u'该账号已被禁用')
            g.user = user
        return f(*args, **kwargs)
    return decorated_function

def expert_required(f):
    """
    专家权限装饰器
    要求：已登录 且 role_type == "2"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. 先进行基础登录校验（确保 g.user 存在）
        if not g.auth_token:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请登录后操作')
        
        user = User.verify_auth_token(g.auth_token, g.app_type)
        if not user:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')
        
        # 2. 校验身份是否为专家 (role_type == "2")
        if str(user.role_type) != "2":
            return error(resid=USER_HAS_NO_PERMISSION, msg=u'权限不足，该操作仅限专家用户')
            
        if user.status == 0:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'该账号已被禁用')
            
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    管理员权限装饰器（针对 User 表中的 role_type == "3"）
    注意：这与你原有的 login_required_admin (DoctorInfo) 逻辑不同，
    这是为了管理非遗项目的普通管理员设计的。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.auth_token:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请登录后操作')
        
        user = User.verify_auth_token(g.auth_token, g.app_type)
        if not user:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')
        
        # 2. 校验身份是否为管理员 (role_type == "3")
        if str(user.role_type) != "3":
            return error(resid=USER_HAS_NO_PERMISSION, msg=u'权限不足，该操作仅限管理员')
            
        if user.status == 0:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'该账号已被禁用')
            
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

def expert_or_admin_required(f):
    """
    专家或管理员权限装饰器（自包含登录校验）
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. 基础 Token 存在性校验
        if not getattr(g, 'auth_token', None):
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请登录后操作')
        
        # 2. 校验 Token 并获取用户
        user = User.verify_auth_token(g.auth_token, getattr(g, 'app_type', 'web'))
        if not user:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')
        
        # 3. 核心角色校验：2-专家, 3-管理员
        if str(user.role_type) not in ["2", "3"]:
            return error(resid=403, msg=u'权限不足，仅限专家或管理员操作')
            
        # 4. 账号禁用状态校验
        if hasattr(user, 'status') and user.status == 0:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'该账号已被禁用')
            
        # 5. 绑定用户到全局对象 g
        g.user = user
        return f(*args, **kwargs)
        
    return decorated_function

# 你原有的 login_required_admin 保持不变，用于 DoctorInfo 的逻辑
def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.auth_token:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请登录后操作')
        admin = DoctorInfo.verify_auth_token(g.auth_token)
        if not admin:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'请退出重新登录')
        if admin.delete is True:
            return error(resid=AUTH_TOKEN_ERROR, msg=u'{}:用户已经被禁用或冻结'.format(USER_NOT_ACTIVE_OR_LOCKED))
        g.admin = admin
        return f(*args, **kwargs)
    return decorated_function

def admin_logger(module, action, id_field='id'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. 执行业务函数
            response = f(*args, **kwargs)

            try:
                # 2. 多种情况解析响应数据 (针对 Flask-RESTful 的兼容)
                res_data = {}
                if hasattr(response, 'get_json'):
                    # 绝大多数情况：jsonify 或 success()/error() 返回的对象
                    res_data = response.get_json() or {}
                elif isinstance(response, dict):
                    # 少数情况：直接返回了字典
                    res_data = response
                elif isinstance(response, tuple):
                    # 情况：返回了 (dict, status_code)
                    res_data = response[0]

                final_status = 1
                final_error_msg = None

                if isinstance(res_data, dict):
                    # 获取业务码
                    biz_resid = res_data.get('resid')
                    # 获取业务状态字符串
                    biz_status_str = res_data.get('status')

                    # 只要满足以下任一条件，即判定为操作失败 (status=0)
                    # 条件1: resid 存在且不等于 200
                    # 条件2: status 字段等于 "error"
                    if (biz_resid is not None and int(biz_resid) != 200) or (biz_status_str == 'error'):
                        final_status = 0
                        final_error_msg = res_data.get('msg', u"业务逻辑拦截")

                # 4. 获取动态 ID 和 Action (由 Service 赋值)
                t_id = getattr(g, 'target_id', None)
                if not t_id:
                    params = request.get_json() if request.is_json else request.values.to_dict()
                    t_id = params.get(id_field) or kwargs.get(id_field)

                t_name = getattr(g, 'target_name', None)
                dynamic_action = getattr(g, 'log_action', action)

                # 5. 写入数据库
                if hasattr(g, 'user') and g.user:
                    AdminLogService.record(
                        admin_id=g.user.id,
                        module=module,
                        action=dynamic_action,
                        target_id=t_id,
                        target_name=t_name,
                        params=request.values.to_dict() if not request.is_json else request.get_json(),
                        status=final_status, # 0 或 1
                        error_msg=final_error_msg
                    )

            except Exception as e:
                # 打印错误到控制台，但不影响接口返回
                import traceback
                print(f"日志系统捕获异常: {traceback.format_exc()}")

            return response
        return decorated_function
    return decorator