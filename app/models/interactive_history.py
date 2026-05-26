# -*- coding: utf-8 -*-
import time
from .base import db

class UserGameHistory(db.Model):
    __tablename__ = 'user_game_history'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'interaction_id', name='uix_u_inter_history'),
        {'comment': '用户互动游玩历史表'}
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id', ondelete='CASCADE'), nullable=False)
    interaction_id = db.Column(db.BigInteger, db.ForeignKey('heritage_interaction.id', ondelete='CASCADE'), nullable=False)
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id'), nullable=False)
    
    # 最近一次游玩时间
    last_play_time = db.Column(db.Integer, default=lambda: int(time.time()))

    # 关联
    interaction = db.relationship('HeritageInteraction')

    @property
    def play_time_str(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.last_play_time))