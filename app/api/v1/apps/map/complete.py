from flask import request
from flask_restful import Resource

from app.api.common.fields import all_completion_fields
from app.api.common.parser import all_completion_parser
from app.api.common.response import success
from app.models.users import User
from app.services.heritage.complete_service import CompletionService


class HeritageAllCompletionResource(Resource):
    """
    独立接口：查询当前用户对所有非遗项目的通关状态
    GET /v1/heritage/completion/all
    """
    def get(self):
        # 1. 获取参数（虽是获取所有，但保留解析器符合规范）
        all_completion_parser()
        
        # 2. 识别用户
        token = request.headers.get('Auth-Token')
        user = User.verify_auth_token(token)
        user_id = user.id if user else None

        status_list = CompletionService.get_all_completion_status(user_id)

        return success(
            msg="获取全量进度成功",
            data={
                "list": status_list,
                "total": len(status_list)
            },
            data_fileds=all_completion_fields()
        )