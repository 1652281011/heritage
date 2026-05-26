from flask import g
from flask_restful import Resource

from app.api.common.parser import work_delete_parser
from app.api.common.response import error, success
from app.services.heritage.game_service import GameService
from app.utils.decorators import login_required


class UserWorkDeleteResource(Resource):
    """
    接口：用户删除自己的互动作品
    POST /v1/user/interact/work/delete
    """
    method_decorators = [login_required]

    def post(self):
        # 1. 解析参数
        args = work_delete_parser()
        
        # 2. 调用 Service 执行删除
        ok, msg = GameService.delete_user_work(
            user_id=g.user.id,
            record_id=args['record_id']
        )
        
        if not ok:
            return error(msg=msg)

        # 3. 返回简洁的成功提示
        return success(msg=msg)