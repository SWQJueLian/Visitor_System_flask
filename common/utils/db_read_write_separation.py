"""
新版的FLASK-SQLALCHEMY只要在构建SQLALCHEMY时，传递session_options给他，告诉它构建session的工厂类即可

self.session = self._make_scoped_session(session_options)


    def _make_scoped_session(
        self, options: dict[str, t.Any]
    ) -> sa.orm.scoped_session[Session]:
        scope = options.pop("scopefunc", _app_ctx_id)
        factory = self._make_session_factory(options)
        return sa.orm.scoped_session(factory, scope)

"""
from __future__ import annotations

import typing as t

import sqlalchemy as sa
import sqlalchemy.exc
import sqlalchemy.orm
from sqlalchemy import UpdateBase, Select

if t.TYPE_CHECKING:
    from flask_sqlalchemy.extension import SQLAlchemy

from flask_sqlalchemy.session import Session


class MYSession(Session):
    """
    查看源码后直接拿到源码这一部分，然后重写get_bind方法，get_bind实际上也是直接复制下来的...
    核心在于其本身有一个_clause_to_engine的方法，通过自己编写一个来实现读写分离
    """
    def get_bind(
            self,
            mapper: t.Any | None = None,
            clause: t.Any | None = None,
            bind: sa.engine.Engine | sa.engine.Connection | None = None,
            **kwargs: t.Any,
    ) -> sa.engine.Engine | sa.engine.Connection:
        """Select an engine based on the ``bind_key`` of the metadata associated with
        the model or table being queried. If no bind key is set, uses the default bind.

        .. versionchanged:: 3.0.3
            Fix finding the bind for a joined inheritance model.

        .. versionchanged:: 3.0
            The implementation more closely matches the base SQLAlchemy implementation.

        .. versionchanged:: 2.1
            Support joining an external transaction.
        """
        if bind is not None:
            return bind

        # 允许手动指定引擎
        # 在查询前设置即可：（玛德，看源码看到我吐血...）
        # db.session.bind = db.get_engine("xxx")
        if self.bind:
            return self.bind
        # engines是由SQLALCHEMY_BINDS和SQLALCHEMY_DATABASE_URI组成，
        # SQLALCHEMY_DATABASE_URI在engines中key为None
        engines = self._db.engines

        if mapper is not None:
            try:
                mapper = sa.inspect(mapper)
            except sa.exc.NoInspectionAvailable as e:
                if isinstance(mapper, type):
                    raise sa.orm.exc.UnmappedClassError(mapper) from e

                raise

            engine = _clause_to_engine(mapper.local_table, engines, self)

            if engine is not None:
                return engine

        if clause is not None:

            engine = _clause_to_engine(clause, engines, self)

            if engine is not None:
                return engine

        if None in engines:
            # None就是SQLALCHEMY_DATABASE_URI指定的默认数据库
            return engines[None]

        return super().get_bind(mapper=mapper, clause=clause, bind=bind, **kwargs)


def _clause_to_engine(
        clause: t.Any | None, engines: t.Mapping[str | None, sa.engine.Engine], session
) -> sa.engine.Engine | None:
    """If the clause is a table, return the engine associated with the table's
    metadata's bind key.
    """
    if isinstance(clause, sa.Table) and "bind_key" in clause.metadata.info:
        # 这个是从模块中读取配置： __bind_key__ = 'master'  # 指定模型访问的数据库
        key = clause.metadata.info["bind_key"]

        # 如果你指定的key不在engines列表中就抛出异常
        if key not in engines:
            raise sa.exc.UnboundExecutionError(
                f"Bind key '{key}' is not in 'SQLALCHEMY_BINDS' config."
            )
        # 如果模型中没有指定
        if key is None:
            # 自己写啦，判断是不是flushing操作 或者是 UpdateBase类和其子类
            # UpdateBase是："""Form the base for ``INSERT``, ``UPDATE``, and ``DELETE`` statements."""
            if session._flushing or isinstance(clause, UpdateBase):
                print("写、改、增操作...使用主库")
                engine = engines["master"]
            else:
                print("其他读操作，使用从库")
                engine = engines["slave"]

            return engine
        else:
            print("模型中指定了使用%s作为数据查询库" % key)
        return engines[key]

    return None
