# -*- coding: utf-8 -*-
import time
from .base import db

class HeritageQuizRecord(db.Model):
    __tablename__ = 'heritage_quiz_record'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'heritage_id', name='uix_user_heritage_quiz'),
        {'comment': '用户非遗答题完成记录表'}
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id', ondelete='CASCADE'), nullable=False)
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id', ondelete='CASCADE'), nullable=False)
    
    # 是否已打通（一旦全对，此状态永久为 1）
    is_finished = db.Column(db.SmallInteger, default=1)
    # 首次完成时间
    finish_time = db.Column(db.Integer, default=lambda: int(time.time()))

    # 关联关系
    user = db.relationship('User', backref=db.backref('quiz_records', lazy='dynamic'))
    heritage = db.relationship('Heritage', backref=db.backref('finished_users', lazy='dynamic'))

    @staticmethod
    def format_timestamp(timestamp):
        """
        静态工具方法：将传入的时间戳格式化为字符串
        供 Service 或其他地方调用
        """
        if not timestamp:
            return ""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

    @property
    def finish_time_str(self):
        """格式化通关时间"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.finish_time))