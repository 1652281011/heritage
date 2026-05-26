# app/api/v1/apps/user/checkin.py
from flask import g
from flask_restful import Resource
from app.api.common.response import success, error
from app.services.user.user_service import UserService
from app.utils.decorators import login_required

class CheckInResource(Resource):
    method_decorators = [login_required]

    def post(self):
        """
        用户签到接口
        POST /v1/user/checkin
        """
        # 调用 Service 处理签到
        ok, res = UserService.perform_checkin(g.user.id)
        
        if ok:
            # 签到成功，返回本次奖励及最新资产
            return success(data=res, msg="签到成功!")
        
        # 如果 ok 为 False，res 里存的是错误原因
        return error(msg=res, resid=400)