import aniso8601
import sqlalchemy as sa
from flask import g
from flask_restful import Resource, reqparse, inputs, abort

from app import db
from app.modules.invite.models import Invite
from app.modules.invite.services import invite_get_all, invite_save, invite_update_by_employee, invite_visitor_arrive
from utils.decorators import login_required_mixin


def datetime_from_iso8601_split_space(datetime_str):
    """用空格切分ISO8601格式的datetime并转换为datetime对象.

    Example::

        inputs.datetime_from_iso8601("2012-01-01 23:30:00+02:00")

    :param datetime_str: The ISO8601-complying string to transform
    :type datetime_str: str
    :return: A datetime
    """
    return aniso8601.parse_datetime(datetime_str, delimiter=' ')


class InviteListApi(Resource):
    method_decorators = [login_required_mixin, ]

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('keyword', required=False, location='args')
        # 由于返回给前端是用空格切分的日期事件，所以前端传回来也是这种格式，此时要处理一下。除非前端处理....都可以解决问题
        # 但是我前端已经写好了，这李主要兼容前端，这玩意不像DRF序列化器，还可以指定格式化的格式
        parser.add_argument('datetime', required=False, location='args', type=datetime_from_iso8601_split_space)
        parser.add_argument('limit', required=False, location='args', default=20, type=int)
        args = parser.parse_args()
        print(args)

        invite_list = invite_get_all({
            "employee_id": g.userid,
            **args,
        })

        results = [x.to_dict(
            only=('id', 'visitor_name', 'visitor_mobile', 'visit_date', 'created_at', 'status')
        ) for x in invite_list]

        data = {
            'results': results
        }

        if len(results) > 0:
            data.setdefault("pre_datetime", results[-1]['created_at'])

        return data


class InviteDetailApi(Resource):
    def get(self, invite_id):
        invite = db.session.scalar(sa.select(Invite).where(Invite.id == invite_id))
        if invite is None:
            abort(404)

        return invite.to_dict()


class InviteCreateApi(Resource):
    method_decorators = [login_required_mixin, ]

    def post(self):
        parser = reqparse.RequestParser()
        # parser.add_argument('employee_id', location='json', required=True, help='员工id必填')
        # parser.add_argument('employee_name', location='json', required=True, help='员工名必填')
        # parser.add_argument('employee_department', location='json', required=True, help='员工所属部门名必填')
        parser.add_argument('visitor_name', location='json', required=True, help='访客名必填')
        parser.add_argument('visitor_mobile', location='json', required=True, help='访客名必填')
        parser.add_argument('visitor_num', location='json', required=False, type=inputs.positive)
        parser.add_argument('visit_date', location='json', required=True,
                            type=datetime_from_iso8601_split_space)
        parser.add_argument('visitor_car_number', location='json', required=False)
        parser.add_argument('visitor_reason', location='json', required=True, help='访客原因必填')
        parser.add_argument('visitor_unit', location='json', required=False)
        args = parser.parse_args()
        print(args)

        employee_id = g.userid

        # employee_data = {
        #     'employee_id': args.pop('employee_id'),
        #     'employee_name': args.pop('employee_name'),
        #     'employee_department': args.pop('employee_department'),
        # }
        # employee = Employee(**employee_data)
        # db.session.add(employee)
        #
        # db.session.flush()

        invite_save(employee_id, args)

        return "InviteCreateApi"


class InviteUpdateApi(Resource):
    def put(self, invite_id):
        parser = reqparse.RequestParser()
        parser.add_argument('visitor_name', location='json', required=True, help='访客名必填')
        parser.add_argument('visitor_mobile', location='json', required=True, help='访客名必填')
        parser.add_argument('visitor_num', location='json', required=False, type=inputs.positive)
        parser.add_argument('visit_date', location='json', required=True, help='来访日期必填')
        parser.add_argument('visitor_car_number', location='json', required=False)
        parser.add_argument('visitor_reason', location='json', required=True, help='访客原因必填')
        parser.add_argument('visitor_unit', location='json', required=False)
        args = parser.parse_args()
        print(args)

        invite_update_by_employee(g.userid, invite_id, args)

        return "InviteUpdateApi"


class InviteStatusUpdateApi(Resource):
    def validate_password(self, val):
        # 暂时写死了....理论上可以开多一个模型类然后允许再后台里面随时修改密码
        if val != '666666':
            raise Exception('密码不正确')
            # raise BusinessException(GlobalStatusCode.PWD_ERR)
        return val

    def put(self, invite_id):
        parser = reqparse.RequestParser()
        parser.add_argument('password', location='json', required=True, type=self.validate_password)
        parser.add_argument('status', location='json', type=int, required=True, choices=(1, 2))
        args = parser.parse_args()

        invite_visitor_arrive(invite_id, args['status'])
