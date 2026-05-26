import time

from flask import g
from sqlalchemy import desc
from app.models import db
from app.models.application import CreatorApplication
from app.models.users import User


class CreatorService:
    @staticmethod
    def submit_application(user, args):
        """
        用户提交申请成为创作者
        逻辑：已是专家不能申，有待审核记录不能申；被驳回后可以再申。
        """
        # 1. 身份校验
        if str(user.role_type) == '2':
            return None, u"您已经是专家身份，无需申请"

        # 2. 状态校验：只检查是否存在“待审核(0)”的申请
        pending_app = CreatorApplication.query.filter_by(
            user_id=user.id, 
            status=0
        ).first()
        
        if pending_app:
            return None, u"您已有申请正在审核中，请勿重复提交"

        # 3. 创建新申请（即便之前有 status=2 的记录，这里也会新增一条）
        try:
            new_app = CreatorApplication(
                user_id=user.id,
                real_name=args['real_name'],
                specialty=args['specialty'],
                reason=args.get('reason'),
                evidence_url=args.get('evidence_url'),
                status=0,
                c_time=int(time.time())
            )
            db.session.add(new_app)
            db.session.commit()
            return new_app, u"申请提交成功，请等待审核"
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    def audit_application(app_id, status, comment):
        """管理员审核创作者入驻申请"""
        # 1. 获取申请记录
        application = CreatorApplication.query.get(app_id)
        if not application:
            return None, u"申请记录不存在"
        
        # 2. 【核心校验】防止重复审核：只要 status 不为 0，说明已经处理过了
        if application.status != 0:
            status_text = u"已通过" if application.status == 1 else u"已驳回"
            return None, f"该申请已被处理过（当前状态：{status_text}），请勿重复操作"

        try:
            # 3. 为日志装饰器挂载动态信息
            g.target_id = app_id
            g.target_name = f"用户:{application.real_name}(UID:{application.user_id})"
            g.log_action = u"通过专家申请" if int(status) == 1 else u"驳回专家申请"

            # 4. 更新申请表状态
            application.status = status
            application.admin_comment = comment
            application.e_time = int(time.time())

            # 5. 若审核通过，同步升级用户表中的 role_type 为 '2' (专家)
            if int(status) == 1:
                target_user = User.query.get(application.user_id)
                if target_user:
                    target_user.role_type = '2'

            # 6. 提交数据库
            db.session.commit()
            return True, u"审核处理成功"
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
        
    @staticmethod
    def get_latest_progress(user_id):
        """
        获取用户最新的入驻申请进度
        """
        # 按创建时间倒序排列，取第一条即为最近的一次申请
        latest_app = CreatorApplication.query.filter_by(user_id=user_id)\
            .order_by(desc(CreatorApplication.c_time))\
            .first()
            
        if not latest_app:
            return None, u"暂无申请记录"
            
        return latest_app, u"查询成功"
    
    @staticmethod
    def get_application_detail(app_id):
        """
        获取申请详情（包含关联的用户对象）
        """
        # 使用 joinedload 或直接查询，SQLAlchemy 会根据 relationship 自动处理
        application = CreatorApplication.query.get(app_id)
        
        if not application:
            return None, u"该申请记录不存在"
            
        return application, u"查询成功"