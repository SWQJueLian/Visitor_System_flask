from collections.abc import Iterable
from json import dumps

from flask import current_app, make_response
from flask_restful.utils import PY3


def output_api_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""

    settings = current_app.config.get('RESTFUL_JSON', {})

    temp_code = code

    if isinstance(data, dict):
        temp_code = data.pop("code", None) or code

    # 判断data中是否有data名称的key，如果有就采用
    if data is not None and isinstance(data, Iterable):
        if "data" in data:
            final_data = data.pop("data")
        else:
            # 没有，没就是本身就是字典或者列表数据啦
            # if data.__len__() > 0:
            final_data = data
            # else:
            #     final_data = None
    else:
        final_data = None

    data = {
        "code": temp_code,
        "message": data.pop("message") if "message" in data else "ok",
        "data": final_data
    }

    # If we're in debug mode, and the indent is not set, we set it to a
    # reasonable value here.  Note that this won't override any existing value
    # that was set.  We also set the "sort_keys" value.
    if current_app.debug:
        settings.setdefault('indent', 4)
        settings.setdefault('sort_keys', not PY3)

    # always end the json dumps with a new line
    # see https://github.com/mitsuhiko/flask/pull/1262
    dumped = dumps(data, **settings) + "\n"

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp