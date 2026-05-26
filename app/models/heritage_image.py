# -*- coding: utf-8 -*-
import time
from flask import current_app
from app.models import db

class HeritageImage(db.Model):
    __tablename__ = 'heritage_image'
    __table_args__ = {'comment': '非遗图片关联表'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    # 关键：直接写表名 'heritage_info.id' 避免导入主模型类
    heritage_id = db.Column(db.BigInteger, 
                            db.ForeignKey('heritage_info.id', ondelete='CASCADE'), 
                            nullable=False, index=True)
    image_url = db.Column(db.String(500), nullable=False)
    # 1-封面图, 2-详情图
    image_type = db.Column(db.SmallInteger, default=2, nullable=False)
    
    # 时间戳使用 Integer 匹配数据库 INT(11)
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))

    @property
    def full_url(self):
        """拼接完整图片访问地址"""
        base_url = current_app.config.get('FILE_BASE_URL', '').rstrip('/')
        if self.image_url:
            path = self.image_url.lstrip('/')
            return f"{base_url}/{path}"
        return None

    def __repr__(self):
        return f'<HeritageImage id={self.id} type={self.image_type}>'