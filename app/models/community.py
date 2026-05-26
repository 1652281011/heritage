# -*- coding: utf-8 -*-
import time
from .base import db, BaseModel

class Post(db.Model, BaseModel):
    __tablename__ = 'post_info'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    
    is_public = db.Column(db.SmallInteger, default=1, comment='1公开, 0私密')
    status = db.Column(db.SmallInteger, default=1, comment='1正常, 0删除')
    
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)

    # 关联关系
    # backref='post' 允许在 PostImage/Comment 中使用 .post 访问对应的 Post 对象
    author = db.relationship('User', backref=db.backref('my_posts', lazy='dynamic'))
    images = db.relationship('PostImage', backref='post', cascade="all, delete-orphan")
    # 这里的 'Comment' 是下方定义的类名，它会自动指向 __tablename__ = 'comment'
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def author_nickname(self):
        return self.author.nickname if self.author else u"匿名用户"

    @property
    def cover_url(self):
        """获取第一张图片作为封面"""
        return self.images[0].url if self.images and len(self.images) > 0 else ""

    @property
    def c_time_str(self):
        """格式化创建时间"""
        if not self.c_time: return ""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.c_time))

    def to_summary_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "images": [img.url for img in self.images],
            "author_nickname": self.author_nickname,
            "create_time": self.c_time_str,
            "is_public": self.is_public,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count
        }

    def to_full_dict(self, current_user_id=None):
        """详情模式"""
        # 判断当前登录用户是否点赞
        is_liked = Like.query.filter_by(user_id=current_user_id, post_id=self.id).first() is not None if current_user_id else False
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "images": [img.url for img in self.images],
            "view_count": self.view_count,
            "like_count": self.like_count, 
            "comment_count": self.comment_count,
            "is_liked": is_liked,
            "author": {
                "nickname": self.author_nickname,
                "avatar": self.author.avatar if self.author else ""
            },
            "create_time": self.c_time_str
        }

class PostImage(db.Model, BaseModel):
    __tablename__ = 'post_image'
    id = db.Column(db.Integer, primary_key=True)
    # 【核心修改】外键指向 post_info.id
    post_id = db.Column(db.Integer, db.ForeignKey('post_info.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)

class Like(db.Model, BaseModel):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    # 【核心修改】外键指向 post_info.id
    post_id = db.Column(db.Integer, db.ForeignKey('post_info.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='_user_post_like_uc'),)

class Comment(db.Model, BaseModel):
    # 【核心修改】确保表名匹配数据库中的 comment
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    # 【核心修改】外键指向 post_info.id
    post_id = db.Column(db.Integer, db.ForeignKey('post_info.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    user = db.relationship('User', backref=db.backref('my_comments', lazy='dynamic'))

    def to_dict(self):
        # 兼容处理 c_time
        ts = self.c_time if self.c_time else int(time.time())
        return {
            "id": self.id,
            "nickname": self.user.nickname if self.user else u"匿名",
            "avatar": self.user.avatar if self.user else "",
            "content": self.content,
            "create_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
        }
    
    @property
    def c_time_str(self):
        """将 c_time 整数时间戳转为标准字符串"""
        # 注意：这里需要确保你的 BaseModel 里有 c_time 字段，或者这里直接用 self.c_time
        if not hasattr(self, 'c_time') or not self.c_time:
            return ""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.c_time))