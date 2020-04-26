import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Items(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    main_characteristics = sqlalchemy.Column(sqlalchemy.TEXT, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    display = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    processor = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    videoadapter = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ram = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    battery = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.VARCHAR, default='/static/images/old.png')
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
