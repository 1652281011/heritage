from flask_restful import Resource

from app.api.common.fields import admin_question_list_fields
from app.api.common.parser import admin_question_query_parser
from app.api.common.response import success
from app.services.heritage.question_request_service import QuestionService
from app.utils.decorators import admin_required


class AdminQuestionListResource(Resource):
    """管理员：管理正式题库列表"""
    method_decorators = [admin_required]
    def get(self):
        args = admin_question_query_parser()
        data = QuestionService.get_admin_live_list(args)
        return success(data=data, data_fileds=admin_question_list_fields())