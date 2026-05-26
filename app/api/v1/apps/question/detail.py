from flask import g, request
from flask_restful import Resource

from app.api.common.fields import question_detail_fields, question_fields
from app.api.common.response import error, success
from app.models.heritage_question import HeritageQuestion
from app.utils.decorators import admin_required


class QuestionDetailResource(Resource):
    method_decorators = [admin_required]
    def get(self):
        r_id = request.args.get('id', type=int)
        req = HeritageQuestion.query.get(r_id)
        return success(data=req, data_fileds=question_detail_fields())