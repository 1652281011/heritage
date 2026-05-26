from flask import g, request
from flask_restful import Resource

from app.api.common.fields import quiz_complete_result_fields
from app.api.common.parser import complete_quiz_parser
from app.api.common.response import error, success
from app.models.users import User
from app.services.heritage.question_service import QuestionService
from app.utils.decorators import login_required


class QuizCompleteResource(Resource):
    """
    提交答题结果接口 (支持游客 & 登录用户)
    """
    
    def post(self):
        # 1. 获取参数
        args = complete_quiz_parser()
        
        # 2. 【核心修改】手动解析 Token，但不拦截
        token = request.headers.get('Auth-Token')
        user = User.verify_auth_token(token)
        user_id = user.id if user else None
        
        # 3. 调用 Service 执行业务逻辑
        result_data, msg = QuestionService.verify_and_submit_quiz(
            user_id=user_id,
            heritage_id=args['heritage_id'],
            answers_list=args['answers']
        )

        if result_data is None:
            return error(msg=msg)

        # 4. 返回统一格式响应
        return success(
            msg=msg,
            data=result_data,
            data_fileds=quiz_complete_result_fields()
        )
