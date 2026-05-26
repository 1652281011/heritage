from flask import g
from flask_restful import Resource

from app.api.common.fields import user_recent_game_fields
from app.api.common.parser import heritage_list_parser, user_recent_games_parser
from app.api.common.response import success
from app.services.heritage.game_service import GameService
from app.utils.decorators import login_required


class UserRecentGamesResource(Resource):
    """
    用户最近游玩记录列表
    GET /v1/user/interact/recent
    """
    method_decorators = [login_required]

    def get(self):
        args = user_recent_games_parser()
        
        result = GameService.get_user_recent_games(
            user_id=g.user.id,
            page=args.get('page', 1),
            per_page=args.get('per_page', 10)
        )
        
        return success(
            msg="获取最近游玩成功",
            data=result,
            data_fileds=user_recent_game_fields()
        )