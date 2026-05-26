from flask import g
from flask_restful import Resource

from app.api.common.fields import game_submit_result_fields
from app.api.common.parser import game_result_submit_parser
from app.api.common.response import success, error
from app.services.heritage.game_service import GameService
from app.utils.decorators import login_required


class InteractionFileResultResource(Resource):
    method_decorators = [login_required]

    def post(self):
        args = game_result_submit_parser()
        
        # 调用 Service，result 会是一个字典
        result, msg = GameService.record_interaction_file(g.user.id, args)
        
        if result is None:
            return error(msg=msg)

        # 直接将 result 字典传给 data
        return success(
            msg=msg,
            data=result, 
            data_fileds=game_submit_result_fields()
        )