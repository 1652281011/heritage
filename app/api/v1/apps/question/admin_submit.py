from flask_restful import Resource

from app.api.common.parser import admin_question_direct_parser
from app.api.common.response import error, success
from app.services.heritage.question_request_service import QuestionService
from app.utils.decorators import admin_logger, admin_required


class AdminQuestionDirectResource(Resource):
    """管理员：直接新增或修改正式题目"""
    method_decorators = [admin_required]
    @admin_logger(module=u"题库管理", action=u"发布题目")
    
    def post(self):
        args = admin_question_direct_parser()
        work, msg = QuestionService.admin_direct_save(args)
        if not work: return error(msg=msg)
        return success(msg=msg)