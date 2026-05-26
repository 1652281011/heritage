import time
from app.models import db
from flask import request
from app.models.admin_log import AdminLog
from sqlalchemy import desc, or_

class AdminLogService:
    @staticmethod
    def get_log_list(args):
        """
        多条件获取日志列表 (支持关键词全表搜索)
        """
        query = AdminLog.query.order_by(desc(AdminLog.c_time))
        
        # 1. 基础字段精准过滤
        if args.get('module'):
            query = query.filter(AdminLog.module == args['module'])
        
        if args.get('admin_id'):
            query = query.filter(AdminLog.admin_id == args['admin_id'])
            
        if args.get('status') is not None:
            query = query.filter(AdminLog.status == args['status'])

        # 2. 【核心】关键词模糊搜索
        keyword = args.get('keyword')
        if keyword:
            # 构造模糊匹配字符串
            search_str = f"%{keyword}%"
            # 同时在 action, module, target_name, params 中搜索
            query = query.filter(or_(
                AdminLog.action.like(search_str),
                AdminLog.module.like(search_str),
                AdminLog.target_name.like(search_str),
                AdminLog.params.like(search_str),
                AdminLog.error_msg.like(search_str)
            ))

        # 3. 执行分页
        pagination = query.paginate(
            page=args['page'], 
            per_page=args['per_page'], 
            error_out=False
        )
        
        return {
            'list': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page
        }
    
    @staticmethod
    def record(admin_id, module, action, target_id=None, target_name=None, params=None, status=1, error_msg=None):
        """核心方法：记录管理员操作日志"""
        try:
            new_log = AdminLog(
                admin_id=admin_id,
                module=module,
                action=action,
                target_id=str(target_id) if target_id else None,
                target_name=target_name,
                params=str(params) if params else None,
                status=status,
                error_msg=error_msg,
                ip_address=request.remote_addr,
                c_time=int(time.time())
            )
            db.session.add(new_log)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            # 仅保留关键异常输出
            import traceback
            traceback.print_exc()
            return False