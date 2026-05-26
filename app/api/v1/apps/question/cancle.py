from flask import g, request
from flask_restful import Resource
from app.models import db

from app.api.common.response import error, success
from app.models.question_request import HeritageQuestionRequest
from app.utils.decorators import expert_required


class QuestionRequestCancelResource(Resource):
    method_decorators = [expert_required]
    def post(self):
        r_id = request.json.get('request_id')
        req = HeritageQuestionRequest.query.filter_by(id=r_id, user_id=g.user.id).first()
        if not req or req.status == 1: return error(msg="无法撤销")
        db.session.delete(req); db.session.commit()
        return success(msg="已撤销")