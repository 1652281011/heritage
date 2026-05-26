# -*- coding: utf-8 -*-
import time, json

from flask import current_app
import urllib
from .base import db

class HeritageRequest(db.Model):
    __tablename__ = 'heritage_request'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    
    # 1-新增申请, 2-修改申请
    req_type = db.Column(db.SmallInteger, nullable=False)
    # 如果是修改，记录对应正式表的ID
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id', ondelete='CASCADE'), nullable=True)
    
    # 用于查重判断的临时名称
    temp_name = db.Column(db.String(100), index=True)
    # 存储全量字段快照 {"heritage_name":..., "introduction":..., "cover_path":..., "detail_paths":[...]}
    content_json = db.Column(db.Text, nullable=False)
    
    # 0-待审核, 1-已通过, 2-已驳回
    status = db.Column(db.SmallInteger, default=0, index=True)
    review_comment = db.Column(db.String(255))
    
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))
    e_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    user = db.relationship('User')
    heritage = db.relationship('Heritage')

    @property
    def data_snap(self):
        """解析快照内容并动态补全图片前缀"""
        if not self.content_json: return {}
        data = json.loads(self.content_json)
        base_url = current_app.config.get('FILE_BASE_URL', '').rstrip('/')

        # 补全封面图 URL
        if data.get('cover_path'):
            path = data['cover_path'].lstrip('/').replace('static/', '', 1)
            data['cover_path'] = f"{base_url}/{urllib.parse.quote(path)}"
        
        # 补全详情图列表 URL
        if data.get('detail_paths'):
            new_paths = []
            for p in data['detail_paths']:
                clean_p = p.lstrip('/').replace('static/', '', 1)
                new_paths.append(f"{base_url}/{urllib.parse.quote(clean_p)}")
            data['detail_paths'] = new_paths
        return data


    @property
    def create_time_str(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.c_time))

    @property
    def update_time_str(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.e_time))
    