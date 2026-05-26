from flask import g, request, send_from_directory
from flask_restful import Resource

from app.api.common.response import error
from app.services.heritage.game_service import GameService
from app.utils.decorators import login_required


class UserWorkDownloadResource(Resource):

    method_decorators = [login_required]

    def get(self):
        # 1. 获取参数
        print("DEBUG: 已经进入了下载接口内部")
        r_id = request.args.get('record_id', type=int)
        if not r_id:
            return error(msg="缺少作品ID")

        # 2. 调用 Service 获取文件物理信息
        file_info, msg = GameService.get_work_file_data(g.user.id, r_id)
        
        if not file_info:
            return error(msg=msg)

        # 3. 核心：发送文件流给前端
        # as_attachment=True 会强制浏览器弹出下载窗口
        # download_name 会让保存的文件名变成用户起的作品名
        return send_from_directory(
            directory=file_info['directory'],
            path=file_info['filename'],
            as_attachment=True,
            download_name=file_info['download_name']
        )