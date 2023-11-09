import os.path
import sys

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from sqlalchemy.exc import OperationalError

from app.settings import constants
from app.settings.configs import config_dict
from flask_apscheduler import APScheduler

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except:
    pass

# 定义一个变量记录项目的根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将common加入到模块搜索路径，pycharm能帮你找，实际部署你就必须要加....
sys.path.append(os.path.join(BASE_DIR, "../common"))

# db对象
# 调用session_options传递自己的Session类，实现读写分离
db = SQLAlchemy()

# APSCHEDULER
scheduler = APScheduler()

# redis
redis_cli: Redis = None


def create_flask_app(env) -> Flask:
    """
    创建app对象并返回
    :param env: 加载指定环境的配置文件
    :return: app实例
    """
    app = Flask(__name__)

    app.config.from_object(config_dict[env])

    # 然后再从环境变量加载覆盖配置（可以用于覆盖配置、或则迷惑别人...比如SECRET_KEY，你并不想别人知道，你就可以用这种方式。）
    # 从环境变量指向的配置文件中读取的配置信息会覆盖掉从配置对象中加载的同名参数
    # slient ： 如果是True则表示即便没有这个环境遍历，也不会抛出异常。默认为False
    app.config.from_envvar(constants.EXTRA_CONFIG_FROM_ENV_NAME,
                           silent=True)  # SECRET_CONFIG变量设置为一个配置文件的相对或者绝对路径，文件里面的配置项是k=v

    # # 返回json
    # # 需要注意的是json默认是会对中文进行ascii编码，需要再flask的配置中设置
    # # flask 2.2之前：
    # # app.config["JSON_AS_ASCII"] = False
    # # flask 2.2之后。原因：2.2提供了一个JsonProvider ： https://github.com/pallets/flask/pull/4692
    # # 拓展：使用orjson，这个json库比较好的样子？有空看看。https://www.jb51.net/article/250451.htm
    # app.json.ensure_ascii = False
    app.json_provider_class.ensure_ascii = app.config.get("ADV_FLASK_ENSURE_ASCII", True)

    return app


def create_app(env):
    """创建app实例的工厂函数"""
    app = create_flask_app(env)

    # 注册扩展组件
    register_extra(app)

    # 注册url路径参数转换器
    # from utils.converters import register_converters
    # register_converters(app)

    # 注册蓝图
    register_blueprint(app)

    # 统一异常处理
    from utils import exceptions
    app.register_error_handler(exceptions.DBException, exceptions.database_error)
    app.register_error_handler(OperationalError, exceptions.operational_error)

    return app


def register_extra(app: Flask):
    """将一些额外的初始化统一放到该方法中"""

    # 初始化数据库
    db.init_app(app)

    # 初始化redis
    global redis_cli
    redis_cli = Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["REDIS_SELECT_DB"],
        decode_responses=True  # 取出来默认decode，就不用自己decode了...
    )
    app.redis_cli = redis_cli
    # 数据迁移
    Migrate(app, db)
    # 导入模型类【一定要记得！】
    from app.modules.invite.models import Invite, Employee

    # 请求钩子注入
    # 每次请求进来之前，判断是否有token，并校验token
    # 将token中的用户id、是否刷新token标志位写入到g对象中，方便后续视图类、视图函数判断是否有登录。
    from utils.middlewares import get_userid
    app.before_request(get_userid)

    ### 跨域， flask-cors ###
    CORS(app)

    # APSCHEDULER
    scheduler.init_app(app)
    scheduler.start()


def register_blueprint(app: Flask):
    """将注册蓝图的操作统一方法这个函数中"""
    from app.modules.invite import invite_bp
    from app.modules.oauth import oauth_bp
    # url_prefix可以在app注册蓝图的时候写，也可以在蓝图对象实例中指定，如：user_blueprint = Blueprint("users", __name__,url_prefix="/user")
    # 如果同时指定，以app.register_blueprint方法中指定的为准
    app.register_blueprint(invite_bp, url_prefix="/invite")
    app.register_blueprint(oauth_bp, url_prefix="/oauth")
