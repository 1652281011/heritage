# -*- coding: utf-8 -*-
import time
import urllib.parse
from flask import current_app, request
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

from .base import db, BaseModel 
from app.utils.uploader import save_upload_file

class User(db.Model, BaseModel):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(30), nullable=False, default="momo")
    avatar = db.Column(db.String(255)) # 数据库建议存储相对路径：uploads/avatars/xxx.jpg
    bio = db.Column(db.String(255))
    
    medal_count = db.Column(db.Integer, default=0)
    heritage_coin = db.Column(db.Integer, default=0)
    experience_progress = db.Column(db.Integer, default=0)
    checkin_days = db.Column(db.Integer, default=0)
    last_checkin_time = db.Column(db.Integer, comment='最后签到时间')
    
    role_type = db.Column(db.String(20), default="1")
    status = db.Column(db.SmallInteger, default=1)

    is_public_collect = db.Column(db.SmallInteger, default=1)
    is_public_like = db.Column(db.SmallInteger, default=1)
    is_public_work = db.Column(db.SmallInteger, default=1)
    is_public_achievement = db.Column(db.SmallInteger, default=1)

    post_count = db.Column(db.Integer, default=0)
    total_like_count = db.Column(db.Integer, default=0)

    # ================= 核心修改：动态头像获取 =================
    @property
    def avatar_url(self):
        """动态拼接，且如果没有头像则返回 None"""
        if not self.avatar:
            return None
        
        # 1. 获取动态 IP 的基础地址 (http://10.x.x.x:39012/static)
        base_url = current_app.config.get('FILE_BASE_URL', '').rstrip('/')
        
        path = self.avatar.lstrip('/')
        if path.startswith('static/'):
            path = path.replace('static/', '', 1)

        # 3. 对中文/空格编码并拼接
        safe_path = urllib.parse.quote(path)
        return "{}/{}".format(base_url, safe_path)

    def check_password(self, password_plain):
        if not self.password: return False
        return check_password_hash(self.password, password_plain)
    
    def _get_redis_token_key(self, app_type):
        return f"{app_type}_{self.id}_auth_token"

    def generate_auth_token(self, expiration=86400, app_type='web'):
        from app import redis_store
        secret = current_app.config.get('SECRET_KEY')
        salt = current_app.config.get('SALT_KEY', 'user-salt')
        s = Serializer(secret_key=secret, salt=salt)
        res = s.dumps({'confirm_id': self.id, 'iat': time.time()})
        auth_token = res.decode('utf-8') if isinstance(res, bytes) else res
        try:
            redis_key = self._get_redis_token_key(app_type)
            redis_store.set(redis_key, auth_token, ex=expiration)
        except Exception as e:
            current_app.logger.error(f"Redis写入失败 [UID:{self.id}]: {e}")
        return auth_token

    def delete_auth_token(self, app_type='web'):
        from app import redis_store
        try:
            return redis_store.delete(self._get_redis_token_key(app_type))
        except Exception as e:
            current_app.logger.error(f"Redis删除失败 [UID:{self.id}]: {e}")
            return False

    @staticmethod
    def verify_auth_token(token, app_type='web'):
        from app import redis_store 
        if not token: return None
        s = Serializer(
            secret_key=current_app.config.get('SECRET_KEY'), 
            salt=current_app.config.get('SALT_KEY', 'user-salt')
        )
        try:
            data = s.loads(token)
            user_id = data.get('confirm_id')
            if not user_id: return None
            redis_key = f"{app_type}_{user_id}_auth_token"
            saved_token = redis_store.get(redis_key)
            if not saved_token: return None
            if isinstance(saved_token, bytes):
                saved_token = saved_token.decode('utf-8')
            if saved_token != token: return None
            return User.query.get(user_id)
        except (SignatureExpired, BadSignature): return None
        except Exception as e:
            current_app.logger.error(f"Token解析异常: {e}")
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            # 使用动态生成的属性 avatar_url
            'avatar': self.avatar_url, 
            'bio': self.bio or "这个用户很懒，什么都没写",
            'medal_count': self.medal_count,
            'heritage_coin': self.heritage_coin,
            'experience_progress': self.experience_progress,
            'checkin_days': self.checkin_days,
            'role_type': self.role_type,
            'privacy': {
                'is_public_collect': bool(self.is_public_collect),
                'is_public_like': bool(self.is_public_like),
                'is_public_work': bool(self.is_public_work),
                'is_public_achievement': bool(self.is_public_achievement),
            },
            'last_login': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.e_time or time.time()))
        }