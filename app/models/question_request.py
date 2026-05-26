# -*- coding: utf-8 -*-
import time, json
from .base import db

class HeritageQuestionRequest(db.Model):
    __tablename__ = 'heritage_question_request'
    __table_args__ = {'comment': '题库新增/修改申请表'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    
    # 1-新增题目, 2-修改题目
    req_type = db.Column(db.SmallInteger, nullable=False)
    # 修改时关联正式题库ID
    question_id = db.Column(db.BigInteger, db.ForeignKey('heritage_question.id', ondelete='CASCADE'), nullable=True)
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id'), nullable=False)
    
    # 存储题目全量快照 JSON: {"q_type":1, "stem":"...", "option_a":..., "answer":"A", "analysis":"..."}
    content_json = db.Column(db.Text, nullable=False)
    
    status = db.Column(db.SmallInteger, default=0, index=True) # 0待审, 1通过, 2驳回
    review_comment = db.Column(db.String(255))
    
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))
    e_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    user = db.relationship('User')
    heritage = db.relationship('Heritage')

    @property
    def data_snap(self):
        return json.loads(self.content_json) if self.content_json else {}

    @property
    def create_time_str(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.c_time))