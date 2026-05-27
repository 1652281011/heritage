import re
import time

from flask import current_app, g
from sqlalchemy import desc, or_
from app.api.common.error_code import USER_IS_EXISTS
from app.models import db
from app.models.users import User
from app.utils.uploader import Uploader

class UserService:
    @staticmethod
    def register(args):
        """注册逻辑"""
        username = args.get('username')
        if not re.match(r'^1[3-9]\d{9}$', str(username)):
            # 这里直接返回 False 和你想要的错误文本
            return False, "MOBILE_TYPE_ERROR"
        # 1. 查重
        if User.query.filter_by(username=args['username']).first():
            return False, "USER_IS_EXISTS"
        
        # 2. 创建用户
        try:
            new_user = User()
            new_user.username = args['username']
            new_user.role_type = args['role_type']
            # 内部通过 generate_password_hash 加密存入 password 字段
            from werkzeug.security import generate_password_hash
            new_user.password = generate_password_hash(args['password'])
            
            # 初始化默认资产
            new_user.medal_count = 0
            new_user.heritage_coin = 0
            new_user.experience_progress = 0
            new_user.checkin_days = 0
            
            # 初始化时间
            now = int(time.time())
            new_user.c_time = now
            new_user.e_time = now
            
            db.session.add(new_user)
            db.session.commit()
            return True, new_user.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def login(args):
        username = args.get('username')
        password = args.get('password')

        # 1. 首先查询用户是否存在
        user = User.query.filter_by(username=username).first()
        if not user:
            # 返回明确的账号不存在信息
            return False, "ACCOUNT_NOT_FOUND"

        # 2. 校验用户状态（是否被封禁）
        if user.status == 0:
            return False, "ACCOUNT_DISABLED"

        # 3. 校验密码是否正确
        if not user.check_password(password):
            # 返回明确的密码错误信息
            return False, "PASSWORD_ERROR"

        # --- 登录成功逻辑 ---
        # 更新数据库最近登录时间 e_time
        current_ts = int(time.time())
        user.e_time = current_ts
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return False, "SYSTEM_ERROR"

        # 生成 Token
        token = user.generate_auth_token()

        # 构造精简的返回数据
        login_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_ts))
        res_data = {
            "username": user.username,
            "nickname": user.nickname,
            "role_type": user.role_type,
            "e_time": login_time_str,
            "auth_token": token
        }
        
        return True, res_data
    
    @staticmethod
    def update_profile(user_id, args):
        """完善并修改用户信息逻辑"""
        user = User.query.get(user_id)
        if not user:
            return False, "用户不存在"

        # 1. 更新文本字段
        if args.get('nickname'): user.nickname = args['nickname']
        if args.get('bio') is not None: user.bio = args['bio']

        # 2. 更新隐私开关 (0/1)
        if args.get('is_public_collect') is not None: user.is_public_collect = args['is_public_collect']
        if args.get('is_public_like') is not None: user.is_public_like = args['is_public_like']
        if args.get('is_public_work') is not None: user.is_public_work = args['is_public_work']
        if args.get('is_public_achievement') is not None: user.is_public_achievement = args['is_public_achievement']

        # 3. 处理头像上传 (调用 Uploader 类)
        avatar_file = args.get('avatar')
        if avatar_file:
            config = {
                "pathFormat": "uploads/avatar/{yyyy}{mm}{dd}/{time}{rand:6}",
                "maxSize": 2 * 1024 * 1024, # 2MB
                "allowFiles": [".png", ".jpg", ".jpeg"],
                "oriName": avatar_file.filename
            }
            uploader = Uploader(avatar_file, config, current_app.static_folder)
            if uploader.stateInfo == "SUCCESS":
                user.avatar = uploader.fullName.lstrip('/') 
            if uploader.stateInfo == "文件类型不允许":
                return False, "FILE_TYPE_NOT_ALLOWED"
            elif uploader.stateInfo == "文件大小超出网站限制":
                return False, "FILE_TOO_BIG"

        # 4. 提交数据库
        try:
            db.session.commit()
            return True, user.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, f"数据库更新失败: {str(e)}"
        
    @staticmethod
    def get_user_profile(target_id):
        # 1. 查找目标用户
        target_user = User.query.get(target_id)
        if not target_user or target_user.status == 0:
            return False, "用户不存在"

        data = target_user.to_dict()
        
        return True, data
    
    def perform_checkin(user_id):
        """用户签到逻辑"""
        user = User.query.get(user_id)
        if not user:
            return False, "用户不存在"

        now_ts = int(time.time())
        
        # 1. 判断是否已经签到过
        if user.last_checkin_time:
            # 将上次签到时间戳和当前时间戳转为 YYYY-MM-DD 格式进行比对
            last_date = time.strftime('%Y-%m-%d', time.localtime(user.last_checkin_time))
            today_date = time.strftime('%Y-%m-%d', time.localtime(now_ts))
            
            if last_date == today_date:
                return False, "今天已经签到过了，明天再来吧"
        
        user.checkin_days += 1
        user.last_checkin_time = now_ts
        
        # 3. 经验/探索进度增加 (示例：每签到一次增加1%)
        if user.experience_progress < 100:
            user.experience_progress += 1

        try:
            db.session.commit()
            # 返回最新的资产情况供前端展示
            return True, {
                "total_days": user.checkin_days
            }
        except Exception as e:
            db.session.rollback()
            return False, f"签到失败: {str(e)}"
        
    @staticmethod
    def get_user_list_admin(args):
        """管理员获取用户分页列表"""
        query = User.query

        # 1. 身份筛选
        if args.get('role_type'):
            query = query.filter(User.role_type == args['role_type'])
        
        # 2. 状态筛选
        if args.get('status') is not None:
            query = query.filter(User.status == args['status'])

        # 3. 关键词模糊搜索 (账号或昵称)
        keyword = args.get('keyword')
        if keyword:
            search_str = f"%{keyword}%"
            query = query.filter(or_(
                User.username.like(search_str),
                User.nickname.like(search_str)
            ))

        # 4. 排序：按注册时间倒序
        query = query.order_by(desc(User.c_time))

        # 5. 执行分页
        pagination = query.paginate(
            page=args['page'], 
            per_page=args['per_page'], 
            error_out=False
        )

        return {
            'list': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page
        }
    
    @staticmethod
    def manage_user_account(admin_user, args):
        """
        管理员管理用户账号（包含冗余操作校验）
        """
        target_id = args['user_id']
        target_user = User.query.get(target_id)
        
        if not target_user:
            return False, u"目标用户不存在"

        # 1. 安全校验：禁止操作自己
        if admin_user.id == target_id:
            return False, u"操作失败：您不能修改自己的账号状态或权限"

        # 2. 【核心】重复/冗余操作校验
        # 记录真正需要修改的字段
        effective_changes = []
        log_details = []

        # 校验状态变更
        req_status = args.get('status')
        if req_status is not None:
            if target_user.status == req_status:
                status_text = u"正常" if req_status == 1 else u"禁用"
                return False, f"操作无效：该用户状态已经是[{status_text}]，无需重复设置"
            else:
                old_status_text = u"正常" if target_user.status == 1 else u"禁用"
                new_status_text = u"正常" if req_status == 1 else u"禁用"
                target_user.status = req_status
                effective_changes.append('status')
                log_details.append(f"状态:{old_status_text}->{new_status_text}")

        # 校验身份变更
        req_role = args.get('role_type')
        if req_role is not None:
            if str(target_user.role_type) == str(req_role):
                role_map = {"1": u"群众", "2": u"专家", "3": u"管理"}
                role_text = role_map.get(str(req_role), req_role)
                return False, f"操作无效：该用户身份已经是[{role_text}]，无需重复设置"
            else:
                old_role = str(target_user.role_type)
                target_user.role_type = str(req_role)
                effective_changes.append('role_type')
                log_details.append(f"身份:{old_role}->{req_role}")

        # 如果没有任何有效的变更字段（比如参数全为空）
        if not effective_changes:
            return False, u"未提供任何需要修改的有效参数"

        try:
            # 3. 挂载日志信息
            g.target_id = target_id
            g.target_name = f"账号:{target_user.username}"
            g.log_action = u"账号管理: " + " | ".join(log_details)

            db.session.commit()
            return True, u"账号管理操作成功"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    @staticmethod
    def logout(user_id, token):
        """
        退出登录逻辑
        :param user_id: 用户ID
        :param token: 当前使用的 Token
        """
        try:
            # 方案 A: 如果你使用了 Redis 存储 Token (推荐)
            redis_client = current_app.extensions['redis']
            redis_client.delete(f"auth_token:{token}")
            
            # 方案 B: 如果你的 Token 是存储在 MySQL 的某个 Session 表中
            # SessionTable.query.filter_by(token=token).delete()
            
            # 方案 C: 如果是简单的 JWT 且没有黑名单机制，前端直接删除 Token 即可
            # 但为了安全，通常建议后端至少记录一个“注销”动作
            
            db.session.commit()
            return True, u"退出成功"
        except Exception as e:
            db.session.rollback()
            return False, str(e)