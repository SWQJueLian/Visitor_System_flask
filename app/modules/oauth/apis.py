from flask import current_app, request
from flask_restful import Resource

from .services import wxwork_generator_access_token, wxwork_get_userinfo


class WxWorkOauthURLGenerateApi(Resource):
    """生成企业微信oauth的链接"""

    WXWORK_STATE = ""  # 不校验state阶段了，给个空就行

    def get(self):
        oauth_url = (
            f"https://open.weixin.qq.com/connect/oauth2/authorize?"
            f"appid={current_app.config['WXWORK_COPRID']}&redirect_uri={current_app.config['WXWORK_REDIRECT_URI']}&response_type=code"
            f"&scope=snsapi_base&state={self.WXWORK_STATE}&agentid={current_app.config['WXWORK_APP_AGENT_ID']}#wechat_redirect"
        )

        return {"oauth_url": oauth_url}


class WxWorkUserInfoApi(Resource):
    def get(self):
        code = request.args.get("code")
        if not code:
            raise Exception("缺少必要参数")
        data = wxwork_get_userinfo(code)
        data["access_token"] = wxwork_generator_access_token(data)
        return data
