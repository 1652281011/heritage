# -*- coding: utf-8 -*-
from flask import g, request
from flask_restful import Resource
from app.api.common import error_code
from app.api.common.response import success, error
from app.api.common.parser import post_detail_parser
from app.api.common.fields import post_detail_fields
from app.models.community import Post, Like
from app.models import db
from app.models.users import User

class PostDetailResource(Resource):
    def get(self):
        """
        获取帖子详情接口 (修复 is_liked 不更新问题)
        """
        # 1. 参数解析
        args = post_detail_parser()
        post_id = args.get('post_id')
        
        # 2. 查询帖子
        post = Post.query.filter_by(id=post_id, status=1).first()
        if not post:
            return error(error_code.POST_NOT_EXISTS, msg=u"帖子内容不存在或已删除")

        # 3. 先执行业务逻辑：增加阅读量并提交
        try:
            post.view_count += 1
            db.session.commit() 
            # 关键：commit 之后，SQLAlchemy 可能会刷新对象，所以我们在此之后再做 is_liked 的判断
        except Exception:
            db.session.rollback()

        # 4. 【核心修复】：手动识别当前访问者身份
        # 既然没有 login_required 强制拦截，我们需要手动从 header 拿一次 Token
        current_user = getattr(g, 'user', None)
        if not current_user:
            token = request.headers.get('Auth-Token')
            if token:
                # 调用你 User 模型里的验证方法
                current_user = User.verify_auth_token(token)

        # 5. 【核心修复】：判断点赞状态
        # 必须确保在 commit 之后赋值，防止被 session 刷新覆盖
        post.is_liked = False 
        if current_user:
            # 这里的 Like 模型对应你 __tablename__ = 'post_like' 的那个类
            exist_like = Like.query.filter_by(
                post_id=post.id, 
                user_id=current_user.id
            ).first()
            
            # 如果能查到记录，则设为 True
            if exist_like:
                post.is_liked = True

        # 6. 返回结果 (marshal 会自动读取 post.is_liked 属性)
        return success(
            msg=u"请求成功",
            data=post, 
            data_fileds=post_detail_fields()
        )