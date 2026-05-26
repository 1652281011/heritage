from flask_restful import Resource

from app.api.common.fields import interaction_review_result_fields
from app.api.common.parser import interaction_audit_action_parser
from app.api.common.response import error, success
from app.services.heritage.interactive_service import InteractionService
from app.utils.decorators import admin_logger, admin_required


class InteractionReviewResource(Resource):
    """
    管理员审核接口 (POST /v1/interact/audit)
    """
    method_decorators = [admin_required]

    @admin_logger(module=u"互动管理", action=u"审核互动", id_field='interaction_id')

    def post(self):
        # 1. 获取并验证参数
        args = interaction_audit_action_parser()
        
        # 2. 执行逻辑（包含自动联动 Heritage 表）
        work, msg = InteractionService.audit_work(
            it_id=args['interaction_id'], 
            status=args['status'], 
            comment=args.get('review_comment')
        )
        
        if not work:
            return error(msg=msg)

        # 3. 返回成功，data_fileds 会自动序列化最新的 status 和 review_comment
        return success(
            msg=msg, 
            data=work, 
            data_fileds=interaction_review_result_fields()
        )