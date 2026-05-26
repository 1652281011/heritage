#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/30 上午8:19
# @Software：PyCharm
# @Author  : scott
from flask import g, current_app
from itsdangerous import URLSafeTimedSerializer  as Serializer, SignatureExpired, BadSignature
from app.models import db
from app.models.base import BaseModel
from app.utils.common import md5_str

from datetime import datetime



class DoctorInfo(db.Model):
    __tablename__ = 'doctor_info'
    __table_args__ = {'comment': '医生/调查者信息表'}

    doctor_id = db.Column(
        db.String(20, collation='utf8mb4_unicode_ci'),
        primary_key=True,  # 根据业务逻辑假设为主键
        nullable=False,
        comment='医生ID'
    )
    doctor_name = db.Column(
        db.String(20, collation='utf8mb4_unicode_ci'),
        nullable=True,
        comment='医生姓名'
    )
    organization = db.Column(
        db.String(100, collation='utf8mb4_unicode_ci'),
        nullable=True,
        comment='所属机构'
    )
    password = db.Column(
        db.String(300, collation='utf8mb4_unicode_ci'),
        nullable=False,
        comment='采取哈希、秘钥等加密算法，有应用确定'
    )
    creation_time = db.Column(
        db.TIMESTAMP,
        nullable=False,
        server_default=db.text('CURRENT_TIMESTAMP'),  # 数据库自动生成时间戳
        comment='创建时间'
    )

    @staticmethod
    def insert_default():
        a = DoctorInfo()
        a.username = u'admin',
        a.password = DoctorInfo.generation_password('Admin2022'),

        db.session.add(a)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return u'error: 插入数据库失败'
        print(u'success')

    @staticmethod
    def generation_password(password):
        import base64
        import random
        rand1 = md5_str(str(random.randint(1000, 9999)))
        rand2 = md5_str(str(random.randint(1000, 9999)))
        _password = rand1[1:-2] + md5_str(base64.b64encode(md5_str(password).encode('utf8'))) + rand2[5: -3]
        return _password

    def generate_auth_token(self, expiration=60 * 60 * 24 * 30):
        """
        生成token供使用 设置有效期
        :param expiration: 有效期
        :return:  auth_token值
        """
        from app import redis_store
        s = Serializer(secret_key=current_app.config['SECRET_KEY'],
                       # expires_in=expiration,
                       salt=current_app.config['SALT_KEY'])
        auth_token = s.dumps({'confirm_id': self.id})#.decode('utf8')

        # 将auth_token保存到redis里面，并设置有效期，验证的时候检查redis中的值，用于废弃auth_token
        redis_store.set('admin_{}_auth_token'.format(self.id), auth_token, expiration)

        return auth_token

    def delete_auth_token(self):
        """从redis中删除auth_token表示无效"""
        from app import redis_store
        redis_store.delete('admin_{}_auth_token'.format(self.id))
        g.user = None
        return True

    @staticmethod
    def verify_auth_token(token):
        """验证token是否有效"""

        s = Serializer(secret_key=current_app.config['SECRET_KEY'],
                       salt=current_app.config['SALT_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            # token超时失效了
            return None
        except BadSignature as e:
            # token错误,具体错误解析可得到: 1.token被篡改　2.token payload不完整
            current_app.logger.exception(e)
            return None
        except Exception as e:
            # 未知的异常错误
            current_app.logger.exception(e)
            return None

        if 'confirm_id' not in data:
            return None

        user_id = data['confirm_id']

        # 判断传输的token与服务器保存的token是都一致
        from app import redis_store
        auth_token = redis_store.get('admin_{}_auth_token'.format(user_id))
        if not auth_token:
            return None

        try:
            admin = DoctorInfo.query.filter_by(id=user_id).first()
        except Exception as e:
            # token保存的用户信息无效的、不存在
            current_app.logger.exception(e)
            return None
        if auth_token != token:
            return None

        return admin

    def to_dict(self):

        res = {
            'auth_token': self.generate_auth_token(),
            'username': self.username,
            'user_id': self.id,
            'b_id': self.b_id
        }

        return res
