from flask import Blueprint
from flask_restful import Api

from .apis import (
    InviteListApi,
    InviteDetailApi,
    InviteCreateApi,
    InviteUpdateApi,
    InviteStatusUpdateApi
)

invite_bp = Blueprint('invite', __name__)

api = Api(invite_bp)

# 为了兼容之前写好的前端，url结尾特意加上/，因为django的是要加的。。。
api.add_resource(InviteListApi, '/')
api.add_resource(InviteDetailApi, '/<invite_id>/')
api.add_resource(InviteCreateApi, '/create/')
api.add_resource(InviteUpdateApi, '/<invite_id>/')
api.add_resource(InviteStatusUpdateApi, '/<invite_id>/status_update/')
