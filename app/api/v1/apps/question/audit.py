from flask_restful import Resource
from flask_restful import reqparse

from app.api.common.response import error, success
from app.services.heritage.question_request_service import QuestionService
from app.utils.decorators import admin_logger, admin_required


class QuestionRequestAuditResource(Resource):
    method_decorators = [admin_required]

    @admin_logger(module=u"题库管理", action=u"审核题目", id_field='request_id')

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('request_id', type=int, required=True, location='json')
        parser.add_argument('status', type=int, required=True, location='json')
        parser.add_argument('review_comment', type=str, location='json')
        args = parser.parse_args()
        ok, msg = QuestionService.audit(args['request_id'], args['status'], args.get('review_comment'))
        return success(msg=msg) if ok else error(msg=msg)