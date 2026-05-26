from flask import g
from flask_restful import Resource

from app.api.common.parser import work_name_update_parser
from app.api.common.response import error, success
from app.services.heritage.game_service import GameService
from app.utils.decorators import login_required


class UserWorkNameUpdateResource(Resource):

    method_decorators = [login_required]

    def post(self):
        # 1. 解析 JSON 参数
        args = work_name_update_parser()
        
        # 2. 调用 Service 执行修改
        record, msg = GameService.update_user_work_name(
            user_id=g.user.id,
            record_id=args['record_id'],
            new_name=args['work_name']
        )
        
        if not record:
            return error(msg=msg)

        # 3. 返回更新后的数据
        return success(
            msg=msg
        )