# -*- coding: utf-8 -*-
import time
from .base import db

class HeritageCollect(db.Model):
    __tablename__ = 'heritage_collect'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'heritage_id', name='uix_user_heritage'),
        {'comment': '用户收藏非遗关联表'}
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id'), nullable=False)
    
    # 收藏时间
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))

    # 建立关联关系（可选，方便查询）
    user = db.relationship('User', backref=db.backref('my_collections', lazy='dynamic'))
    heritage = db.relationship('Heritage', backref=db.backref('collected_by', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'heritage_id': self.heritage_id,
            'collect_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time))
        }