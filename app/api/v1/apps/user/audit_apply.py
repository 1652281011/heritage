from flask_restful import Resource

from app.api.common.parser import creator_audit_parser
from app.api.common.response import error, success
from app.services.user.application import CreatorService
from app.utils.decorators import admin_logger, admin_required


class CreatorAuditResource(Resource):
    """
    POST /v1/admin/creator/audit
    管理员审核申请
    """
    method_decorators = [admin_required]

    @admin_logger(module=u"用户管理", action=u"审核专家申请", id_field='application_id')

    def post(self):
        args = creator_audit_parser()
        work, msg = CreatorService.audit_application(
            app_id=args['application_id'],
            status=args['status'],
            comment=args.get('admin_comment')
        )
        
        if not work:
            return error(msg=msg)
            
        return success(msg=msg)