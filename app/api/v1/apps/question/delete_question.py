from flask_restful import Resource

from app.api.common.parser import admin_question_delete_parser
from app.api.common.response import error, success
from app.services.heritage.question_request_service import QuestionService
from app.utils.decorators import admin_logger, admin_required


class AdminQuestionDeleteResource(Resource):
    """管理员：批量删除题目"""
    method_decorators = [admin_required]
    @admin_logger(module=u"题库管理", action=u"批量删除题目")
    def post(self):
        args = admin_question_delete_parser()
        ok, msg = QuestionService.admin_batch_delete(args['question_ids'])
        return success(msg=msg) if ok else error(msg=msg)