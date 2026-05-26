# -*- coding: utf-8 -*-
import time
from flask import current_app
from .base import db

class Achievement(db.Model):
    """成就配置表：定义勋章及其达成条件"""
    __tablename__ = 'achievement_definition'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False) # 1-探索, 2-知识, 3-互动
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(255), nullable=False) # 存储相对路径
    
    target_value = db.Column(db.Integer, nullable=False) # 目标数值
    stat_dimension = db.Column(db.String(50), nullable=False) # quiz_count | collect_count | game_count

    CATEGORY_MAP = {1: "文化探索", 2: "知识达人", 3: "非遗护法人"}

    @property
    def category_name(self):
        return self.CATEGORY_MAP.get(self.category, "未知")

    @property
    def icon_url(self):
        base_url = current_app.config.get('FILE_BASE_URL', '').rstrip('/')
        return f"{base_url}/{self.icon.lstrip('/')}" if self.icon else ""

class UserStat(db.Model):
    """进度统计表：记录用户各维度的当前数值"""
    __tablename__ = 'user_stat'
    __table_args__ = (db.UniqueConstraint('user_id', 'stat_key', name='uix_user_stat'),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    stat_key = db.Column(db.String(50), nullable=False) # 与 stat_dimension 对应
    current_value = db.Column(db.Integer, default=0)

class UserAchievement(db.Model):
    """成就记录表：记录用户已解锁的勋章"""
    __tablename__ = 'user_achievement'
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='uix_user_ach'),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement_definition.id'), nullable=False)
    unlock_time = db.Column(db.Integer, default=lambda: int(time.time()))

    achievement = db.relationship('Achievement', backref='earned_records')