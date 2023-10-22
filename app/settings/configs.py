class DefaultConfig:
    # 使用flask中的session要配置SECRET_KEY
    SECRET_KEY = "asGd87fghC-8-8rddd89uAEQCXC3$x.x.xa4sdas"

    # 这个变量是自定义的，用来确保Flask默认的response返回jsop字符串确保不经过ascii编码
    ADV_FLASK_ENSURE_ASCII = False

    # restful-json返回中文不经过ascii编码
    RESTFUL_JSON = {
        "ensure_ascii": False
    }

    ### SQLALCHEMY配置相关 ###
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/vistor"


    # 显示ORM执行的SQL语句
    SQLALCHEMY_ECHO = False

    # 如果启用，将记录请求期间每个查询的信息。使用get_recorded_queries()获取请求期间发出的查询列表。
    # 用于分析慢查询
    SQLALCHEMY_RECORD_QUERIES = False

    # 跟踪，关闭它，不然有性能影响
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ### JWT配置相关 ###
    # JWT SECRET KEY
    JWT_SECRET_KEY = 'xiuagTFxgx..ADFEaiuxdbjas$#$1%$$&8-12du91234562'

    NGROK_SUBDOMAN = 'https://3ae2-116-22-20-85.ngrok-free.app'

    #### 企业微信相关信息 ####
    WXWORK_COPRID = 'ww04ecc3032787ebc3'
    WXWORK_APP_SECRET = 'avr_EJqaiVBqBvSB4QD0F2F9ZMO4e-_F607GBF6rJQQ'
    WXWORK_APP_AGENT_ID = '1000003'
    WXWORK_REDIRECT_URI = NGROK_SUBDOMAN + '/wxwork-oauth'

    ### 跨越设置 ###
    # 让flask-cors直接读取配置文件。
    CORS_ORIGINS = [
        "http://127.0.0.1:8080",
        "https://127.0.0.1:8080",
        "http://127.0.0.1:5000",
        "https://127.0.0.1:5000",
        NGROK_SUBDOMAN
    ]
    CORS_MAX_AGE = 86400
    CORS_SUPPORTS_CREDENTIALS = True


    #### APScheduler ####
    # 这个和flask中的jsonify()函数有关，但是不知道为啥默认应该就是True的，FLASK-APScheduler会找不到，所以手动设置一下。。
    JSONIFY_PRETTYPRINT_REGULAR = True

    # 开启API查询功能，给你提供了很多接口，是Flask-APScheduler额外提供的功能
    SCHEDULER_API_ENABLED = True
    # api接口的前缀，默认是/schedule
    # SCHEDULER_API_PREFIX: str(default: "/scheduler")
    SCHEDULER_API_PREFIX = "/apscheduler"
    # SCHEDULER_ENDPOINT_PREFIX: str(default: "scheduler.")
    # 允许访问的主机
    # SCHEDULER_ALLOWED_HOSTS: list(default: ["*"])


class DevConfig(DefaultConfig):
    DEBUG = True

    # 显示ORM执行的SQL语句
    SQLALCHEMY_ECHO = True

    # 如果启用，将记录请求期间每个查询的信息。使用get_recorded_queries()获取请求期间发出的查询列表。
    # 用于分析慢查询
    SQLALCHEMY_RECORD_QUERIES = False

    # REDIS信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_SELECT_DB = 8

    # 定义redis集群的Node节点信息
    # 注意不一定要全部集群的节点信息都放在这里，因为RedisCluster只要求集群中其中一个节点即可！
    # REDIS_CLUSTER_NODES = [
    #     {"host": "192.168.2.6", "port": 7000},
    #     {"host": "192.168.2.6", "port": 7001},
    #     {"host": "192.168.2.6", "port": 7002},
    # ]



class ProductConfig(DefaultConfig):
    DEBUG = False

    # REDIS信息
    REDIS_HOST = "10.0.1.140"
    REDIS_PORT = 30817
    REDIS_SELECT_DB = 0


class TestConfig(DefaultConfig):
    DEBUG = True


config_dict = {
    "dev": DevConfig,
    "prod": ProductConfig,
    "test": TestConfig,
}
