from flask import Blueprint
from flask_restful import Api
from utils.funstools import output_api_json

from app.api.urls import define_urls

from .urls import urlpatterns

# from .apis import (
#     InviteListApi,
#     InviteDetailApi,
#     InviteCreateApi,
#     InviteUpdateApi,
#     InviteStatusUpdateApi
# )

invite_bp = Blueprint("invite", __name__)

api = Api(invite_bp)

# 其他： 统一api json输出格式
api.representation("application/json")(output_api_json)

# 为了兼容之前写好的前端，url结尾特意加上/，因为django的是要加的。。。
# api.add_resource(InviteListApi, '/')
# api.add_resource(InviteDetailApi, '/<invite_id>/')
# api.add_resource(InviteCreateApi, '/create/')
# api.add_resource(InviteUpdateApi, '/<invite_id>/')
# api.add_resource(InviteStatusUpdateApi, '/<invite_id>/status_update/')

# 模仿django，将url统一放到一个文件中。
define_urls(api, urlpatterns)
