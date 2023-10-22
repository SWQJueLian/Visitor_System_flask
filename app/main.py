import os

from app import create_app

# 通过环境变量设置项目运行时使用的配置文件，这里就手动设置以下了，一般部署的时候通过脚本等设置。
# os.environ.setdefault("APP_ENV", "dev")

app = create_app(os.environ.get("APP_ENV", "dev"))


@app.route('/')
def all_route():
    """返回所有路由信息,调试用..."""
    rules = app.url_map.iter_rules()
    print(os.environ.get("APP_ENV"))
    return [i.__repr__() for i in rules]
