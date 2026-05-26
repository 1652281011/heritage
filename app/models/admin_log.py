# -*- coding: utf-8 -*-
import time
from .base import db

class AdminLog(db.Model):
    __tablename__ = 'admin_operation_log'
    __table_args__ = {'comment': '管理员全模块操作审计表'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    
    # 模块枚举：非遗、互动、题库、专家审核、账号管理、社区治理
    module = db.Column(db.String(50), nullable=False)
    # 行为：新增、修改、审核通过、驳回、封禁、删除
    action = db.Column(db.String(50), nullable=False)
    
    # 被操作对象的信息
    target_id = db.Column(db.String(50))    # 被操作对象的ID (如 heritage_id)
    target_name = db.Column(db.String(100)) # 被操作对象的名称/昵称 (如 "藏戏" 或 "用户A")
    
    ip_address = db.Column(db.String(50))
    params = db.Column(db.Text)             # 请求参数快照
    
    status = db.Column(db.SmallInteger, default=1) # 1-成功, 0-异常
    error_msg = db.Column(db.Text)
    
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))

    admin = db.relationship('User')

    @property
    def create_time_str(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.c_time))