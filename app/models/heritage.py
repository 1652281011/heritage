# -*- coding: utf-8 -*-
import time
from app.models import db

class Heritage(db.Model):
    __tablename__ = 'heritage_info'
    __table_args__ = {'comment': '非遗基本信息表'}

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    heritage_name = db.Column(db.String(100), nullable=False, unique=True)
    heritage_class = db.Column(db.String(50))
    origin = db.Column(db.String(100))
    spread_region = db.Column(db.String(100), nullable=False)
    brief_intro = db.Column(db.String(500))
    introduction = db.Column(db.Text)
    enroll_year = db.Column(db.String(20), index=True)
    tags = db.Column(db.String(255))
    is_interact = db.Column(db.Boolean, default=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=True)

    # 关联申请人
    author = db.relationship('User', backref=db.backref('heritage_applications', lazy='dynamic'))

    view = db.Column(db.Integer, default=0)
    collect = db.Column(db.Integer, default=0)

    # 时间戳使用 Integer
    c_time = db.Column(db.Integer, default=lambda: int(time.time()))
    e_time = db.Column(db.Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    # 关联：使用字符串 'HeritageImage'，SQLAlchemy 会在初始化时自动查找对应类
    images = db.relationship(
        'HeritageImage',
        backref=db.backref('heritage_owner', lazy='joined'),
        lazy='dynamic', # 方便在 property 中使用 filter
        cascade='all, delete-orphan'
    )
    @property
    def cover_url(self):
        """获取封面图"""
        # 局部导入防止循环引用
        from app.models.heritage_image import HeritageImage
        cover = self.images.filter(HeritageImage.image_type == 1).first()
        if cover:
            return cover.full_url
        # 无封面则返回第一张
        first = self.images.first()
        return first.full_url if first else None

    @property
    def image_list(self):
        """获取除封面外的细节图列表"""
        from app.models.heritage_image import HeritageImage
        imgs = self.images.filter(HeritageImage.image_type == 2).all()
        return [img.full_url for img in imgs]
    
    @property
    def tag_list(self):
        if self.tags:
            # 兼容处理：将中文顿号、中文逗号全部替换为英文逗号
            raw_tags = self.tags.replace('、', ',').replace('，', ',')
            # 按照英文逗号拆分，并去掉每个标签前后的空格，过滤掉空字符串
            return [t.strip() for t in raw_tags.split(',') if t.strip()]
        return [] # 如果数据库为空，返回空列表
    
    @property
    def create_time_str(self):
        """将 c_time 整数时间戳转为标准字符串"""
        if not self.c_time:
            return ""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.c_time))
    
    @property
    def update_time_str(self):
        """将 e_time 整数时间戳转为标准字符串"""
        if not self.e_time:
            return ""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.e_time))

    def __repr__(self):
        return f'<Heritage {self.heritage_name}>'