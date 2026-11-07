from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def make_engine(url: str) -> Engine:
    return create_engine(
        url,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"connect_timeout": 3},
    )


def make_sessions(engine: Engine):
    return sessionmaker(engine, expire_on_commit=False)
