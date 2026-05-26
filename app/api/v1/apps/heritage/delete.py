from flask_restful import Resource

from app.api.common.parser import heritage_delete_parser
from app.api.common.response import error, success
from app.services.heritage.heritage_service import HeritageService
from app.utils.decorators import admin_logger, admin_required


class HeritageDeleteResource(Resource):
    """
    接口：管理员彻底删除已发布的非遗项目
    POST /v1/heritage/delete
    """
    method_decorators = [admin_required]

    # module: 模块名
    # action: 默认动作名
    # id_field: 对应参数中的 heritage_id，用于装饰器防抖指纹计算
    @admin_logger(module=u"非遗管理", action=u"删除非遗", id_field='heritage_id')
    def post(self):
        # 1. 解析参数
        args = heritage_delete_parser()
        
        # 2. 调用 Service 执行删除
        work, msg = HeritageService.delete_heritage(h_id=args['heritage_id'])
        
        # 3. 返回结果
        if not work:
            return error(msg=msg)
            
        return success(msg=msg)