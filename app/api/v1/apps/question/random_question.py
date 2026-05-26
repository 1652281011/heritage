from flask_restful import Resource

from app.api.common.fields import question_fields
from app.api.common.parser import question_list_parser
from app.api.common.response import success,error
from app.services.heritage.question_service import QuestionService


class QuestionRandomResource(Resource):
    def get(self):

        args = question_list_parser()
        questions = QuestionService.get_random_questions(args['heritage_id'], limit=3)
        if not questions:
            return error(msg="暂无题目")
        return success(msg="获取成功", data=questions, data_fileds=question_fields())