from flask import g
from flask_restful import Resource

from app.api.common.fields import heritage_history_fields
from app.api.common.parser import heritage_list_parser, user_browsing_history_parser
from app.api.common.response import success
from app.services.heritage.heritage_service import HeritageService
from app.utils.decorators import login_required


class UserBrowsingHistoryResource(Resource):
    """
    我的足迹接口
    GET /v1/user/heritage/history
    """
    method_decorators = [login_required]

    def get(self):
        # 复用之前的 list_parser 获取 page, per_page
        args = user_browsing_history_parser() 
        
        result = HeritageService.get_user_browsing_history(
            user_id=g.user.id,
            page=args.get('page', 1),
            per_page=args.get('per_page', 10)
        )
        
        return success(
            msg="获取足迹成功",
            data=result,
            data_fileds=heritage_history_fields()
        )