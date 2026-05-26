from flask_restful import Resource

from app.api.common.fields import interaction_list_fields
from app.api.common.parser import interaction_by_heritage_parser
from app.api.common.response import success
from app.services.heritage.interactive_service import InteractionService


class HeritageInteractionListResource(Resource):
    """
    用户接口：查看某项非遗关联的所有已发布互动
    GET /v1/interact/heritage_list?heritage_id=xxx
    """
    def get(self):
        # 1. 解析参数
        args = interaction_by_heritage_parser()
        
        # 2. 调用服务层逻辑，锁定 status=1
        result = InteractionService.get_published_by_heritage(
            heritage_id=args['heritage_id'],
            page=args['page'],
            per_page=args['per_page']
        )
        
        # 3. 返回响应 (注意拼写 data_fileds)
        return success(
            msg="获取非遗互动列表成功",
            data=result,
            data_fileds=interaction_list_fields()
        )