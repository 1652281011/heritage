# -*- coding: utf-8 -*-
import time
from .base import db

class UserBrowsingHistory(db.Model):
    __tablename__ = 'user_browsing_history'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'heritage_id', name='uix_user_h_history'),
        {'comment': '用户浏览历史记录表'}
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id', ondelete='CASCADE'), nullable=False)
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id', ondelete='CASCADE'), nullable=False)
    
    # 浏览时间
    view_time = db.Column(db.Integer, default=lambda: int(time.time()))

    # 建立关联，方便直接拿非遗信息
    heritage = db.relationship('Heritage')

    @property
    def view_time_str(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.view_time))