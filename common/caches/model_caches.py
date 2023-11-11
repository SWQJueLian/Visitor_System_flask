import random

from caches.constants import *

from app import db, redis_cli
from app.modules.invite.models import Employee, Invite


class BaseModelCache:
    """缓存层基类"""

    def __init__(self, *args, **kwargs):
        self.default_random_end = DEFAULT_RANDOM_END

    def get(self, *args, **kwargs):
        """获取"""
        raise NotImplementedError("get Method Not Implemented")

    def update_or_delete(self, *rags, **kwargs):
        """更新或删除，主要看场景：集合类型的比较适合更新，因为一直删除创建性能不好，意义不大。"""
        raise NotImplementedError("update_or_delete Method Not Implemented")

    def get_random_time(self):
        """获取随机缓存时间，进行叠加，防止缓存雪崩"""
        return random.randint(0, self.default_random_end)


class InviteCache(BaseModelCache):
    """访客缓存类"""

    def __init__(self, invite_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 覆盖默认的随机缓存时间范围end值
        self.default_random_end = INVITE_CACHE_RANDOM_RANGE_END
        # invite id
        self.invite_id = invite_id
        # redis key
        self.key = f"invite:{self.invite_id}:info"

    def get(self, serializer_rules=(), serializer_only=(), *args, **kwargs):
        """
        获取对象

        :param serializer_rules 序列化规则
        :param serializer_only 序列化只加载哪些字段
        """
        # 1.先从redis缓存中读取
        invite_info = redis_cli.hgetall(self.key)

        # 2.判断缓存中是否有数据
        if not invite_info:
            # 3.缓存中没有数据，从数据库中读取数据，然后进行缓存回填
            # invite: Invite = db.session.query(Invite).options(joinedload(Invite.employee, innerjoin=True)).filter(
            #     Invite.id == self.invite_id).first()
            invite: Invite = db.session.get(Invite, self.invite_id)

            # 4.读不到数据也要进行缓存，防止缓存穿透。不过缓存时间设置短一些。
            #   本身缓存层的作用就是为了给数据库添加一层保护，当缓存查询不到就要差数据库，如果被利用，当频繁调用缓存中没有的数据，缓存层的意义就失效
            #   了，如果瞬时流量大，全部压力都给到数据库。因此，即便数据不存再也缓存，不过缓存时间短一些，起到保护的作用，也不至于缓存太长时间。
            if invite is None:
                redis_cli.hset(self.key, "none", "1")  # 这里value是随意的，因到时候我判断key是否in就可以了。

                # 缓存时间加上随机时长，防止缓存雪崩
                redis_cli.expire(
                    self.key, time=NONE_INVITE_CACHE_EXPIRE + self.get_random_time()
                )

            # 5.如果能从数据库中读取数据，则进行缓存回填
            invite_info = invite.to_dict(
                rules=serializer_rules, only=serializer_only
            )  # 调用sqlalchemy_serializer的方法序列化对象。
            redis_cli.hset(self.key, mapping=invite_info)
            redis_cli.expire(
                self.key, time=INVITE_CACHE_EXPIRE + self.get_random_time()
            )

        # 如果存在none就是属于缓存击穿（就是第4步的作用），直接在这里就处理了，返回一个空字典。
        if "none" in invite_info:
            invite_info = {}

        return invite_info

    def update_or_delete(self, *args, **kwargs):
        # 因为invite对象是hash类型直接删除即可，集合类型进行update操作比较合适。
        redis_cli.delete(self.key)


class EmployeeCache(BaseModelCache):
    """员工缓存类"""

    def __init__(self, invite_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 覆盖默认的随机缓存时间范围end值
        self.default_random_end = EMPLOYEE_CACHE_RANDOM_RANGE_END
        # invite id
        self.employee_id = invite_id
        # redis key
        self.key = f"employee:{self.employee_id}:info"

    def get(self, serializer_rules=(), serializer_only=(), *args, **kwargs):
        """
        获取对象

        :param serializer_rules 序列化规则
        :param serializer_only 序列化只加载哪些字段
        """

        # 1.先从redis缓存中读取
        employee_info = redis_cli.hgetall(self.key)

        # 2.判断缓存中是否有数据
        if not employee_info:
            # 3.缓存中没有数据，从数据库中读取数据，然后进行缓存回填
            # invite: Invite = db.session.query(Invite).options(joinedload(Invite.employee, innerjoin=True)).filter(
            #     Invite.id == self.invite_id).first()
            employee: Employee = (
                db.session.query(Employee)
                .where(Employee.employee_id == self.employee_id)
                .first()
            )

            # 4.读不到数据也要进行缓存，防止缓存穿透。不过缓存时间设置短一些。
            #   本身缓存层的作用就是为了给数据库添加一层保护，当缓存查询不到就要差数据库，如果被利用，当频繁调用缓存中没有的数据，缓存层的意义就失效
            #   了，如果瞬时流量大，全部压力都给到数据库。因此，即便数据不存再也缓存，不过缓存时间短一些，起到保护的作用，也不至于缓存太长时间。
            if employee is None:
                redis_cli.hset(self.key, "none", "1")  # 这里value是随意的，因到时候我判断key是否in就可以了。

                # 缓存时间加上随机时长，防止缓存雪崩
                redis_cli.expire(
                    self.key, time=NONE_EMPLOYEE_CACHE_EXPIRE + self.get_random_time()
                )
            else:
                # 5.如果能从数据库中读取数据，则进行缓存回填
                employee_info = employee.to_dict(
                    rules=serializer_rules, only=serializer_only
                )  # 调用sqlalchemy_serializer的方法序列化对象。
                redis_cli.hset(self.key, mapping=employee_info)
                redis_cli.expire(
                    self.key, time=EMPLOYEE_CACHE_EXPIRE + self.get_random_time()
                )

        # 如果存在none就是属于缓存击穿（就是第4步的作用），直接在这里就处理了，返回一个空字典。
        if "none" in employee_info:
            employee_info = {}

        return employee_info

    def update_or_delete(self, *rags, **kwargs):
        # 因为employee对象是hash类型直接删除即可，集合类型进行update操作比较合适。
        redis_cli.delete(self.key)
