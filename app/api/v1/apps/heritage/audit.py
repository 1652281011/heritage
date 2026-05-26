from flask_restful import Resource

from app.api.common.parser import heritage_audit_action_parser
from app.api.common.response import error, success
from app.services.heritage.heritage_request_service import HeritageRequestService
from app.utils.decorators import admin_logger, admin_required


class HeritageRequestAuditResource(Resource):
    method_decorators = [admin_required]
    
    @admin_logger(module=u"非遗管理", action=u"审核项目申请", id_field='request_id')

    def post(self):
        args = heritage_audit_action_parser()
        work, msg = HeritageRequestService.audit(args['request_id'], args['status'], args.get('review_comment'))
        return success(msg=msg) if work else error(msg=msg)