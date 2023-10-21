from flask_restful import Resource


class InviteListApi(Resource):
    def get(self):
        return "InviteListApi"


class InviteDetailApi(Resource):
    def get(self, invite_id):
        return "InviteDetailApi"


class InviteCreateApi(Resource):
    def post(self):
        return "InviteCreateApi"


class InviteUpdateApi(Resource):
    def put(self, invite_id):
        return "InviteUpdateApi"
