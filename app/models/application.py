# -*- coding: utf-8 -*-
from app.models import db
import time

class CreatorApplication(db.Model):
    __tablename__ = 'creator_application'
    __table_args__ = {'comment': '创作者入驻申请表'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    specialty = db.Column(db.String(100), nullable=False) # 专业领域
    reason = db.Column(db.Text) # 申请理由
    evidence_url = db.Column(db.String(255)) # 证明材料
    status = db.Column(db.SmallInteger, default=0) # 0-待审核, 1-通过, 2-驳回
    admin_comment = db.Column(db.String(255)) # 管理员备注
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))
    e_time = db.Column(db.Integer, onupdate=lambda: int(time.time()))

    # 关联用户信息
    user = db.relationship('User', backref=db.backref('creator_requests', lazy='dynamic'))

    @property
    def create_time_str(self):
        """将 c_time 整数时间戳转为标准字符串"""
        if not self.c_time:
            return ""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.c_time))
    
    @property
    def update_time_str(self):
        """将 e_time 整数时间戳转为标准字符串"""
        # 如果审核时间 e_time 为 0 或 None，返回“待处理”或空
        if not self.e_time:
            return "待处理"
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.e_time))