# -*- coding: utf-8 -*-
import time
from app.models import db

class HeritageQuestion(db.Model):
    __tablename__ = 'heritage_question'
    __table_args__ = {'comment': '非遗问答题库表'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id'), nullable=False)
    
    # 题型: 1-单选, 2-多选, 3-判断
    q_type = db.Column(db.Integer, default=1, nullable=False)
    stem = db.Column(db.Text, nullable=False, comment='题干内容')
    
    # 选项设计
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=True)
    option_d = db.Column(db.String(255), nullable=True)
    option_count = db.Column(db.Integer, default=4)
    
    # 答案与解析 (答案存 "A" 或 "ABC")
    answer = db.Column(db.String(50), nullable=False)
    analysis = db.Column(db.Text, comment='答案解析')

    # 时间戳
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))
    e_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    # 关联非遗主表
    heritage = db.relationship('Heritage', backref=db.backref('questions', lazy='dynamic'))

    @property
    def create_time_format(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.c_time))