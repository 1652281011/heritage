# -*- coding: utf-8 -*-
import time
from flask import current_app
from sqlalchemy import or_
from app.models import db
from app.models.community import Like, Post, PostImage
from app.models.users import User
from app.utils.uploader import Uploader, save_upload_file
from sqlalchemy.orm import joinedload

class PostService:
    @staticmethod
    def get_post_list(page=1, per_page=10, keyword=None, user_id=None, liked_by_user_id=None, is_own=False):
        """
        通用的获取帖子列表函数
        :param user_id: 指定查询某个用户的发帖
        :param liked_by_user_id: 指定查询某个用户点赞过的帖子
        :param is_own: 是否为查看自己的列表 (如果是，则显示私密帖子)
        """
        # 1. 基础查询：未删除
        query = Post.query.filter_by(status=1)

        # --- 核心修改：增加逻辑筛选 ---
        
        # 场景 A: 查询某人发布的帖子
        if user_id:
            query = query.filter(Post.user_id == user_id)
            # 如果不是看自己的，只能看公开的
            if not is_own:
                query = query.filter(Post.is_public == 1)
        
        # 场景 B: 查询某人点赞过的帖子
        elif liked_by_user_id:
            # 联表 Like 模型，筛选点赞人 ID，且必须是公开的贴
            query = query.join(Like).filter(Like.user_id == liked_by_user_id, Post.is_public == 1)
            
        # 场景 C: 社区公共列表
        else:
            query = query.filter(Post.is_public == 1)

        # 2. 模糊搜索
        if keyword:
            query = query.filter(or_(
                Post.title.like(f'%{keyword}%'),
                Post.content.like(f'%{keyword}%')
            ))

        # 3. 性能优化与排序
        query = query.options(joinedload(Post.author), joinedload(Post.images))\
                     .order_by(Post.c_time.desc())

        # 4. 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "list": pagination.items,
            "total": pagination.total,
            "page": page,
            "per_page": per_page
        }

    @staticmethod
    def create_post(user_id, title, content, image_files=None, is_public=1):
        """
        创建帖子的核心业务函数
        集成了方案二：自动更新 user_info 表的 post_count
        """
        current_ts = int(time.time())
        
        # --- 1. 获取用户信息 ---
        user = User.query.get(user_id)
        if not user:
            return False, u"操作失败：用户不存在"

        # --- 2. 实例化帖子对象 ---
        new_post = Post()
        new_post.user_id = user_id
        new_post.title = title
        new_post.content = content
        new_post.is_public = is_public
        new_post.c_time = current_ts
        new_post.e_time = current_ts

        try:
            # --- 3. 核心事务逻辑 ---
            db.session.add(new_post)
            
            # 【冗余字段维护】：发布成功，该用户的总动态数 +1
            # 使用 getattr 处理可能为 None 的情况，或者确保数据库默认值为 0
            user.post_count = (user.post_count or 0) + 1
            
            # 同步到数据库获取 new_post.id
            db.session.flush()

            # --- 4. 处理多图上传 ---
            if image_files:
                for file_obj in image_files:
                    config = {
                        "pathFormat": "uploads/post/{yyyy}{mm}{dd}/{time}{rand:6}",
                        "maxSize": 5 * 1024 * 1024,
                        "allowFiles": [".png", ".jpg", ".jpeg"]
                    }
                    uploader = Uploader(file_obj, config, current_app.static_folder)
                    
                    if uploader.stateInfo == "SUCCESS":
                        new_img = PostImage(
                            post_id=new_post.id,
                            url=uploader.getFileInfo()['url'],
                            c_time=current_ts,
                            e_time=current_ts
                        )
                        db.session.add(new_img)
                    else:
                        # 只要有一张图片失败，触发回滚
                        db.session.rollback()
                        return False, f"图片上传失败: {uploader.stateInfo}"

            # --- 5. 提交并刷新 ---
            db.session.commit()
            db.session.refresh(new_post) 
            
            return True, new_post.to_summary_dict()

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"PostService Create Error: {str(e)}")
            return False, u"数据库保存失败"

    @staticmethod
    def delete_post(post_id, user_id, is_admin=False): # <--- 核心修复：添加 is_admin 参数
        """
        删除帖子并维护用户统计数据
        """
        # 1. 查找帖子
        post = Post.query.get(post_id)
        if not post:
            return False, u"帖子不存在"

        # 2. 权限校验：如果不是管理员，且不是作者本人，则无权删除
        if not is_admin and post.user_id != user_id:
            return False, u"无权删除他人的帖子"

        # 3. 获取作者对象用于更新计数器
        author = User.query.get(post.user_id)

        try:
            # 维护冗余字段逻辑 (方案二)
            if author:
                author.post_count = max(0, (author.post_count or 1) - 1)
                author.total_like_count = max(0, (author.total_like_count or 0) - post.like_count)

            # 执行删除
            db.session.delete(post)
            db.session.commit()
            return True, u"删除成功"

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Delete Post Error: {str(e)}")
            return False, u"数据库操作失败"
        
    @staticmethod
    def update_post(post_id, user_id, title=None, content=None, is_public=None):
        """
        修改帖子文本信息逻辑
        """
        # 1. 查找帖子并严格校验权：只有作者本人能改
        post = Post.query.filter_by(id=post_id, user_id=user_id, status=1).first()
        if not post:
            return False, u"帖子不存在或无权修改"

        try:
            # 2. 修改文本和状态 (判断 None 是为了允许修改为空字符串，但 is_public 必须有明确值)
            if title is not None: post.title = title
            if content is not None: post.content = content
            if is_public is not None: post.is_public = is_public
            
            # 3. 记录修改时间
            post.e_time = int(time.time())

            db.session.commit()
            
            # 4. 刷新对象，确保返回给前端的数据是最新的
            db.session.refresh(post)
            return True, post.to_summary_dict()

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update Post Error: {str(e)}")
            return False, u"数据库保存失败"