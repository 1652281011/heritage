from re import error
from flask_restful import Resource

from app.api.common.fields import verify_result_fields
from app.api.common.parser import answer_verify_parser
from app.api.common.response import success
from app.services.heritage.question_service import QuestionService


class AnswerVerifyResource(Resource):
    def post(self):

        args = answer_verify_parser()
        question, is_correct = QuestionService.verify_answer(args['question_id'], args['user_answer'])
        if not question:
            return error(msg="题目不存在")
        
        question.is_correct = is_correct # 动态绑定结果
        return success(msg="校验完成", data=question, data_fileds=verify_result_fields())