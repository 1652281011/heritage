# -*- coding: utf-8 -*-
import time, urllib.parse
from flask import current_app
from .base import db

class HeritageInteraction(db.Model):
    __tablename__ = 'heritage_interaction'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id'), nullable=False)
    description = db.Column(db.Text)
    
    entry_url = db.Column(db.String(500), nullable=False)
    # 封面图相对路径
    cover = db.Column(db.String(255)) 
    
    author_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    status = db.Column(db.SmallInteger, default=0) # 0:待审, 1:发布, 2:驳回
    review_comment = db.Column(db.String(255))
    view_count = db.Column(db.Integer, default=0)
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))

    # 关联
    heritage = db.relationship('Heritage', backref=db.backref('inter_works', lazy='dynamic'))
    author = db.relationship('User', backref=db.backref('inter_contributions', lazy='dynamic'))

    @property
    def heritage_title(self): return self.heritage.heritage_name if self.heritage else ""
    @property
    def author_name(self): return self.author.nickname if self.author else ""

    @property
    def create_time_format(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.c_time))

    @property
    def full_cover_url(self):
        """封面图依然支持动态 IP 适配"""
        if not self.cover: return None
        base_url = current_app.config.get('FILE_BASE_URL', '').rstrip('/')
        clean_path = self.cover.lstrip('/').replace('static/', '', 1)
        return f"{base_url}/{urllib.parse.quote(clean_path)}"