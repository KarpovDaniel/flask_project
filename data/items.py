import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Items(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    main_characteristics = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    specifications = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    user = orm.relation('User')
