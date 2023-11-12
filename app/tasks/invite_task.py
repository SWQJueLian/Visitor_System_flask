import time

from flask import current_app

from app import db, scheduler
from app.modules.invite.models import Invite
from app.modules.oauth.tools.wxwork_tools import WXWorkApi


def send_notify_to_employee(invite_id):
    with scheduler.app.app_context():
        invite: Invite = db.session.get(Invite, invite_id)
        api = WXWorkApi()
        api.send_arrive_markdown_msg(current_app.config["WXWORK_APP_AGENT_ID"], invite)


def send_sms_to_vistor(mobile):
    # 调用短信SDK发送短信
    print(f"向手机号【{mobile}】发送访客链接")
    time.sleep(10)
    print("发送完成！")
