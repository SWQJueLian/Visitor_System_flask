from flask import Blueprint
from flask_restful import Api
from utils.funstools import output_api_json

from app.modules.oauth.apis import WxWorkOauthURLGenerateApi, WxWorkUserInfoApi

oauth_bp = Blueprint("oauth", __name__)

# 为了兼容之前写好的前端，url结尾特意加上/，因为django的是要加的。。。
api = Api(oauth_bp)

# 其他： 统一api json输出格式
api.representation("application/json")(output_api_json)

api.add_resource(WxWorkOauthURLGenerateApi, "/wxwork/")
api.add_resource(WxWorkUserInfoApi, "/wxwork/userinfo/")
