# -*- coding: utf-8 -*-
import time
from flask import current_app, g
from app.models.base import db
from app.models.heritage_interaction import HeritageInteraction
from app.models.heritage import Heritage
from app.models.interactive_history import UserGameHistory
from app.utils.uploader import Uploader, save_upload_file

class InteractionService:
    @staticmethod
    def contribute(user, args):
        """
        专家或管理员投稿接口
        :param user: 当前登录的 User 对象 (g.user)
        """
        # 1. 权限基础校验（虽然Resource层有拦截，Service层双重保险）
        role = str(user.role_type)
        if role not in ["2", "3"]:
            return None, u"权限不足，无法发布互动"

        # 2. 封面图上传逻辑
        cover_rel = None
        if args.get('cover_file'):
            config = {
                "pathFormat": "uploads/inter/{yyyy}{mm}{dd}/{time}{rand:6}", 
                "maxSize": 5*1024*1024, 
                "allowFiles": [".png", ".jpg", ".jpeg", ".webp"], 
                "oriName": args['cover_file'].filename
            }
            up = Uploader(args['cover_file'], config, current_app.static_folder)
            if up.stateInfo == "SUCCESS": 
                cover_rel = up.fullName.lstrip('/')

        # 3. 【核心逻辑修改】：判断身份设定状态
        # 假设 3 是管理员，2 是专家
        is_admin = (role == "3")
        target_status = 1 if is_admin else 0
        msg = u"发布成功" if is_admin else u"投稿成功，请等待审核"

        try:
            work = HeritageInteraction(
                author_id=user.id, 
                heritage_id=args['heritage_id'], 
                name=args['name'],
                description=args.get('description'), 
                entry_url=args['entry_url'], 
                cover=cover_rel,
                status=target_status # 动态设定状态
            )
            db.session.add(work)
            
            # 4. 如果是管理员直接发布，需要同步更新非遗主表的 is_interact 状态
            if is_admin:
                db.session.flush() # 拿到当前事务中的变更，但不提交
                InteractionService._sync_heritage_interact_status(work.heritage_id)

            db.session.commit()

            # --- 【日志记录点】仅为管理员挂载信息 ---
            if is_admin:
                g.target_id = work.id
                g.target_name = work.name
                g.log_action = u"直接发布互动作品"
                
            return work, msg
        except Exception as e:
            db.session.rollback()
            return None, str(e)
        
    @staticmethod
    def _sync_heritage_interact_status(heritage_id):
        """内部辅助：同步非遗主表的互动状态"""
        count = HeritageInteraction.query.filter_by(
            heritage_id=heritage_id, 
            status=1
        ).count()
        
        heritage = Heritage.query.get(heritage_id)
        if heritage:
            heritage.is_interact = (count > 0)
        return count

    @staticmethod
    def audit_work(it_id, status, comment=None):
        work = HeritageInteraction.query.get(it_id)
        if not work:
            return None, u"找不到该互动项目"

        if int(status) == 3 and work.status != 1:
            return None, u"操作失败：只有已上架的作品才能执行下架操作"

        try:
            # --- 【日志记录点】准备动态数据 ---
            g.target_id = it_id
            g.target_name = work.name
            # 根据状态动态定义日志中的动作名称
            log_action_map = {1: u"审核通过", 2: u"审核驳回", 3: u"下架作品"}
            g.log_action = log_action_map.get(int(status), u"审核操作")
            # -------------------------------

            old_status = work.status
            work.status = status
            if comment is not None:
                work.review_comment = comment

            if old_status == 1 or int(status) == 1:
                db.session.flush() 
                InteractionService._sync_heritage_interact_status(work.heritage_id)

            db.session.commit()
            
            msg_map = {1: u"审核通过并已上架", 2: u"审核已驳回", 3: u"作品已成功下架"}
            return work, msg_map.get(int(status), u"操作成功")
            
        except Exception as e:
            db.session.rollback()
            return None, f"数据库操作失败: {str(e)}"
        
    @staticmethod
    def update_work(user_id, it_id, args):
        """专家修改个人投稿"""
        work = HeritageInteraction.query.filter_by(id=it_id, author_id=user_id).first()
        if not work:
            return None, u"作品不存在或无权修改"

        # 1. 更新文本字段
        if args.get('name'): work.name = args['name']
        if args.get('description'): work.description = args['description']
        if args.get('entry_url'): work.entry_url = args['entry_url']

        # 2. 处理封面图更新
        if args.get('cover_file'):
            config = {"pathFormat": "uploads/inter/{yyyy}{mm}{dd}/{time}{rand:6}", "maxSize": 2*1024*1024, 
                      "allowFiles": [".png", ".jpg", ".jpeg"], "oriName": args['cover_file'].filename}
            up = Uploader(args['cover_file'], config, current_app.static_folder)
            if up.stateInfo == "SUCCESS":
                work.cover = up.fullName.lstrip('/')

        # 3. 关键逻辑：修改后必须重新审核
        old_status = work.status
        work.status = 0 

        try:
            db.session.commit()
            # 【关键】：直接返回 work 模型对象本身
            return work, u"修改成功，已重新提交审核" 
        except Exception as e:
            db.session.rollback()
            return None, str(e)
        
    @staticmethod
    def get_published_by_heritage(heritage_id, page=1, per_page=10):
        """
        获取指定非遗项目下所有【已上架(status=1)】的互动列表
        """
        query = HeritageInteraction.query.filter_by(
            heritage_id=heritage_id, 
            status=1
        )
        
        # 按时间倒序排列
        pagination = query.order_by(HeritageInteraction.c_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'list': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def cancel_work(user_id, it_id):
        """
        专家撤销自己的投稿
        逻辑：仅限 status 为 0 (待审核) 或 2 (已驳回) 的作品可以撤销删除
        """
        # 1. 查找作品并确保属于该专家
        work = HeritageInteraction.query.filter_by(id=it_id, author_id=user_id).first()
        if not work:
            return False, u"找不到该互动项目或您无权操作"

        # 2. 状态校验：已上架 (status=1) 或 已下架 (status=3) 的作品不允许直接撤销
        # 如果是 1 或 3，通常需要走“申请下架”或由管理员操作
        if work.status == 1:
            return False, u"作品已通过审核并上架，无法撤销。如需下架请联系管理员。"
        
        try:
            h_id = work.heritage_id
            # 3. 从数据库物理删除或逻辑删除记录
            db.session.delete(work)
            db.session.commit()

            # 4. 安全起见，同步一下非遗主表的状态
            # 防止极特殊情况下删除的是该非遗唯一的互动内容
            InteractionService._sync_heritage_interact_status(h_id)
            db.session.commit()

            return True, u"撤销投稿成功"
        except Exception as e:
            db.session.rollback()
            return False, f"操作失败: {str(e)}"

    @staticmethod
    def get_list(user_id=None, **kwargs):
        """统一列表查询"""
        query = HeritageInteraction.query
        if user_id: query = query.filter_by(author_id=user_id)
        if kwargs.get('status') is not None: query = query.filter_by(status=kwargs['status'])
        if kwargs.get('heritage_id'): query = query.filter_by(heritage_id=kwargs['heritage_id'])
        
        pag = query.order_by(HeritageInteraction.c_time.desc()).paginate(
            page=kwargs.get('page', 1), per_page=kwargs.get('per_page', 10), error_out=False)
        return {'list': pag.items, 'total': pag.total}
        