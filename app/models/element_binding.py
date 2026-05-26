# -*- coding: utf-8 -*-
from app.models import db

class ElementBinding(db.Model):
    __tablename__ = 'element_binding'
    __table_args__ = {'comment': '地图板块与非遗关联表'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    # 对应地图插件或前端定义的板块ID，如 "region_beijing"
    bind_element_id = db.Column(db.String(100), nullable=False, unique=True, index=True)
    # 关联非遗ID
    heritage_id = db.Column(db.BigInteger, db.ForeignKey('heritage_info.id'), nullable=True)
    # 是否激活（展示）
    is_active = db.Column(db.Boolean, default=True)

    # 建立关系，方便在查询板块时直接获取非遗名称等信息
    heritage = db.relationship('Heritage', backref=db.backref('element_bindings', lazy='dynamic'))

    def __repr__(self):
        return f'<ElementBinding {self.bind_element_id} -> {self.heritage_id}>'