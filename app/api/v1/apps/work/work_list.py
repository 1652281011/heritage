from flask import g
from flask_restful import Resource

from app.api.common.fields import user_work_advanced_list_fields
from app.api.common.parser import user_works_search_parser
from app.api.common.response import error, success
from app.services.heritage.game_service import GameService
from app.utils.decorators import login_required


class UserWorkSearchResource(Resource):

    def get(self):
        # 1. 获取解析后的参数
        args = user_works_search_parser()
        
        # 2. 确定目标用户 ID（优先从参数取，没传则看自己）
        viewer = getattr(g, 'user', None)
        target_user_id = args.get('user_id') or (viewer.id if viewer else None)
        
        if not target_user_id:
            return error(msg="请指定要查看的用户ID")

        # 3. 调用 Service (传入 3 个参数)
        result, msg = GameService.get_user_works_advanced(target_user_id, viewer, args)
        
        # 4. 校验结果
        if result is None:
            return error(msg=msg)
            
        return success(
            msg="获取作品集成功",
            data=result,
            data_fileds=user_work_advanced_list_fields()
        )