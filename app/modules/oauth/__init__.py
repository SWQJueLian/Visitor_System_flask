from flask import Blueprint
from flask_restful import Api

from app.modules.oauth.apis import WxWorkOauthURLGenerateApi, WxWorkUserInfoApi

oauth_bp = Blueprint("oauth", __name__)

# 为了兼容之前写好的前端，url结尾特意加上/，因为django的是要加的。。。
api = Api(oauth_bp)
api.add_resource(WxWorkOauthURLGenerateApi, '/wxwork/')
api.add_resource(WxWorkUserInfoApi, '/wxwork/userinfo/')
