from .apis import (
    InviteListApi,
    InviteDetailApi,
    InviteCreateApi,
    InviteUpdateApi,
    InviteStatusUpdateApi
)

# 模仿django的方式，将url的定义抽取出来
urlpatterns = [
    ('/', InviteListApi),
    ('/<invite_id>/', InviteDetailApi),
    ('/create/', InviteCreateApi),
    ('/<invite_id>/', InviteUpdateApi),
    ('/<invite_id>/status_update/', InviteStatusUpdateApi),
]
