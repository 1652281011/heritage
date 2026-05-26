from flask import g, request
from flask_restful import Resource

from app.api.common.fields import request_detail_fields
from app.api.common.response import error, success
from app.models.question_request import HeritageQuestionRequest
from app.utils.decorators import login_required


class QuestionRequestDetailResource(Resource):
    method_decorators = [login_required]
    def get(self):
        r_id = request.args.get('id', type=int)
        req = HeritageQuestionRequest.query.get(r_id)
        if not req or (str(g.user.role_type) != "3" and req.user_id != g.user.id):
            return error(msg="无权查看")
        return success(data=req, data_fileds=request_detail_fields())