from flask import g
from flask_restful import Resource
from sqlalchemy import or_
from app.models.base import db

from app.api.common.fields import request_list_fields
from app.api.common.parser import heritage_request_search_parser
from app.api.common.response import success
from app.models.heritage_edit import HeritageRequest
from app.models.users import User
from app.utils.decorators import login_required


class HeritageRequestListResource(Resource):
    method_decorators = [login_required]
    def get(self):
        args = heritage_request_search_parser()
        is_admin = str(g.user.role_type) == "3"
        
        query = db.session.query(HeritageRequest).join(User, HeritageRequest.user_id == User.id)
        if not is_admin: query = query.filter(HeritageRequest.user_id == g.user.id)
        if args.get('status') is not None: query = query.filter(HeritageRequest.status == args['status'])
        if args.get('user_keyword') and is_admin:
            k = f"%{args['user_keyword']}%"
            query = query.filter(or_(User.nickname.like(k), User.username.like(k)))
        if args.get('heritage_keyword'):
            query = query.filter(HeritageRequest.temp_name.like(f"%{args['heritage_keyword']}%"))

        pag = query.order_by(HeritageRequest.c_time.desc()).paginate(page=args['page'], per_page=10)
        return success(data={'list': pag.items, 'total': pag.total}, data_fileds=request_list_fields())
