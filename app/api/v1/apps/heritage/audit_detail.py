from flask import g, request
from flask_restful import Resource

from app.api.common.fields import request_detail_fields
from app.api.common.response import error, success
from app.models.heritage_edit import HeritageRequest
from app.utils.decorators import login_required


class HeritageRequestDetailResource(Resource):
    method_decorators = [login_required]

    def get(self):
        # 1. 获取 ID
        r_id = request.args.get('id', type=int)
        if not r_id:
            return error(msg="缺少申请单ID参数")

        # 2. 查询记录
        req = HeritageRequest.query.get(r_id)
        if not req:
            return error(msg="该申请记录不存在")

        # 3. 权限校验
        # 逻辑：如果是管理员(role_type=3) 或者是 申请人本人(user_id一致) 才能看
        is_admin = str(g.user.role_type) == "3"
        is_owner = req.user_id == g.user.id

        if not (is_admin or is_owner):
            # 只有既不是管理员也不是本人时，才报权限不足
            return error(msg="权限不足，您只能查看自己提交的申请")

        # 4. 返回成功
        return success(data=req, data_fileds=request_detail_fields())