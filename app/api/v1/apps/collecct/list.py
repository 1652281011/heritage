from flask import g
from flask_restful import Resource

from app.api.common.fields import heritage_list_fields
from app.api.common.parser import collect_list_parser
from app.api.common.response import error, success
from app.services.heritage.collect_service import HeritageCollectService
from app.utils.decorators import login_required


class HeritageCollectListResource(Resource):

    def get(self):
        # 1. 获取解析参数
        args = collect_list_parser()
        
        # 2. 获取当前访问者信息 (关键：不强制要求登录)
        # 如果未登录，g.user 会由你的登录中间件通过 getattr 设置为 None
        viewer = getattr(g, 'user', None)
        
        # 3. 确定查询目标
        # 优先取参数里的 user_id（看别人），如果没有参数则看自己（viewer.id）
        target_user_id = args.get('user_id')
        
        if not target_user_id:
            if viewer:
                target_user_id = viewer.id
            else:
                # 如果既没传 user_id 也没登录，报错告知需要参数
                return error(msg="请指定查询的目标用户ID")

        # 4. 调用 Service 传入权限上下文
        result, msg = HeritageCollectService.get_user_collect_list(
            target_user_id=target_user_id,
            viewer=viewer,
            page=args.get('page', 1),
            per_page=args.get('per_page', 10)
        )

        # 5. 统一结果处理
        if result is None:
            return error(msg=msg)

        return success(
            msg="获取收藏列表成功",
            data=result,
            data_fileds=heritage_list_fields()
        )