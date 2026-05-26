from flask import g
from flask_restful import Resource
from app.models.users import User
from app.api.common.response import success, error
from app.api.common.parser import user_password_update_parser, user_update_parser
from app.utils.decorators import login_required

class UserPasswordResource(Resource):
    method_decorators = [login_required]

    def post(self):
        args = user_password_update_parser()
        ok, res = User.update_password(
            g.user.id, args['old_password'], args['new_password']
        )
        return success(msg=res) if ok else error(msg=res, resid=401)