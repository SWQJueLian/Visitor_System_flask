from flask_restful import Api


def define_urls(api: Api, urlpatterns):
    for item in urlpatterns:
        api.add_resource(item[1], item[0])
