from datetime import timedelta

from flask_restful import Resource

from utils.jwt_tools import generate_token


class WxWorkOauthURLGenerateApi(Resource):
    def get(self):
        pass


class WxWorkUserInfoApi(Resource):
    def get(self):
        # 测试...
        userinfo = {
            'userid': 'SongWeiQuan'
        }
        token = generate_token(userinfo, timedelta(hours=2))
        return token
