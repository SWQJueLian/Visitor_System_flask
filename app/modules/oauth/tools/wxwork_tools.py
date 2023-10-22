import logging

import requests


from flask import current_app
from redis import Redis
from requests import Response

# from common.exceptions.cust_exception import BusinessException

from app.modules.invite.models import Invite

"""
1. 获取token
"""
log = logging.getLogger(__name__)


class BaseWXWorkApi:
    CACHE_KEY = 'access_token'

    def __init__(self, coprid=None, app_secret=None):
        """
        初始化，需要传递coprid 和 app_secret
        :param coprid:
        :param app_secret:
        """
        self._coprid = coprid or current_app.config['WXWORK_COPRID']
        self._app_secret = app_secret or current_app.config['WXWORK_APP_SECRET']
        # self._access_token = None

    @property
    def access_token(self):
        # 干...存到内存缓存算了，也没必要redis...性能没啥影响
        # 如果空则马上获取一个
        # if self._access_token is None:
        #     self.refresh_access_token()
        # return self._access_token
        redis_cli: Redis = current_app.redis_cli

        access_token = redis_cli.get(self.CACHE_KEY)
        if access_token is None:
            print('access_token为空，刷新获取token')
            return self.refresh_access_token()
        return access_token

    def refresh_access_token(self):
        """刷新access_token"""
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        params = {
            "corpid": self._coprid,
            'corpsecret': self._app_secret
        }
        ret_data = self.httpSend(url, params=params)
        access_token = ret_data.get('access_token')
        # 如果要存进redis中，可以参考，一般是这里的秒-30秒比较正常，可以减1分钟或者更多
        expires = ret_data.get('expires_in') or 7200
        redis_cli: Redis = current_app.redis_cli
        redis_cli.set(self.CACHE_KEY, access_token, ex=expires - 60)
        return access_token

    @staticmethod
    def is_token_expired(errcode) -> bool:
        """判断返回状态码是否为400014 和 42001 ，此时token过期"""
        return errcode == 40014 or errcode == 42001

    def httpSend(self, url, params=None, data=None, send_type='GET', body_type='JSON') -> dict:
        """
        :param url:
        :param params:
        :param data:
        :param send_type: 发送类型，GET或者POST
        :param body_type: 默认为JSON，如果是普通请求体，传DATA
        :return:
        """
        print('URL: ', url)
        print('params: ', params)
        print('data: ', data)
        """发送请求，会循环3次来尝试获取响应，返回字典格式的响应体"""
        for i in range(3):
            print(f'发送第{i}次请求')
            if send_type == 'GET':
                response: Response = requests.get(url, params=params, data=data)
            if send_type == 'POST':
                print('发送的是POST请求')
                if body_type == 'JSON':
                    response: Response = requests.post(url, params=params, json=data)
                else:
                    response: Response = requests.post(url, params=params, data=data)
                print('request url: ', response.request.url)
            json_data = response.json()
            print(f"{json_data=}")
            errcode = json_data.get('errcode')
            # 判断token是否过期
            if self.is_token_expired(errcode):
                self.refresh_access_token()
                log.info('企业微信access_token过期，重新获取。')
                continue
            # 不过其，但是状态码不为0，直接抛出业务异常，并记录日志
            if errcode != 0:
                # 记录异常
                log.error(f'请求企业微信api异常，errcode不为0, 返回内容：{json_data}')
                # raise BusinessException(detail='请求企业微信api异常')
                raise Exception('请求企业微信api异常')
            return json_data


class WXWorkApi(BaseWXWorkApi):
    def get_basic_userinfo(self, code):
        """
        根据code获取用户基本信息
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo'
        params = {
            'access_token': self.access_token,
            "code": code
        }
        resp_data = self.httpSend(url, params=params)
        return resp_data

    def get_detail_userinfo(self, userid: str):
        """
        根据userid获取用户详细信息
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get'
        params = {
            'access_token': self.access_token,
            "userid": userid
        }
        resp_data = self.httpSend(url, params=params)
        return resp_data

    def get_detail_department(self, userid: str):
        """
        获取部门详情
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/department/get'
        params = {
            'access_token': self.access_token,
            "id": userid
        }
        resp_data = self.httpSend(url, params=params)
        return resp_data

    def send_arrive_markdown_msg(self, agentid, invite: Invite):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        params = {
            'access_token': self.access_token,
        }
        data = {
            "touser": invite.employee.employee_id,
            "msgtype": "markdown",
            "agentid": agentid,
            "markdown": {
                "content": f"""您邀约的访客`{invite.visitor_name}`, 已到达园区！
> **邀约详情**
> 访客姓名：<font color=\"info\">{invite.visitor_name}</font>
> 来访日期：<font color=\"warning\">{invite.visit_date.strftime('%Y-%m-%d %H:%M:%S')}</font>
> 
> 请您准备接待！"""
            },
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 30
        }
        resp_data = self.httpSend(url, params=params, data=data, send_type='POST')
        return resp_data
