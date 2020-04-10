import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Basket(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'basket'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    item_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("items.id"))
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=1)
    photo = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    user = orm.relation('User')
