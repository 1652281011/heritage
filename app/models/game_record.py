# -*- coding: utf-8 -*-
import time, urllib.parse
from flask import current_app
from .base import db

class HeritageGameRecord(db.Model):
    __tablename__ = 'heritage_game_record'
    # 移除了 UniqueConstraint

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id', ondelete='CASCADE'), nullable=False)
    interaction_id = db.Column(db.BigInteger, db.ForeignKey('heritage_interaction.id', ondelete='CASCADE'), nullable=False)
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id', ondelete='CASCADE'), nullable=False)
    
    work_name = db.Column(db.String(100))
    work_path = db.Column(db.String(255)) 
    file_type = db.Column(db.SmallInteger) # 1-图片, 2-音频, 3-视频
    finish_time = db.Column(db.Integer, default=lambda: int(time.time()))

    # 关联关系
    heritage = db.relationship('Heritage')
    interaction = db.relationship('HeritageInteraction')

    @property
    def full_work_url(self):
        if not self.work_path: return None
        base_url = current_app.config.get('FILE_BASE_URL', '').rstrip('/')
        path = self.work_path.lstrip('/').replace('static/', '', 1)
        return f"{base_url}/{urllib.parse.quote(path)}"

    @property
    def finish_time_str(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.finish_time))