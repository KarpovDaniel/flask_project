from flask import Flask, render_template, redirect, request, abort, jsonify
from flask_restful import reqparse, abort, Api, Resource

from data import db_session, items, users, basket


def abort_if_item_not_found(item_id):
    session = db_session.create_session()
    item = session.query(items.Items).get(item_id)
    if not item:
        abort(404, message=f"Item {item_id} not found")


class ItemResource(Resource):
    def get(self, item_id):
        abort_if_item_not_found(item_id)
        session = db_session.create_session()
        item = session.query(items.Items).get(item_id)
        return jsonify({'item': item.to_dict(
            only=('title', 'price', 'main_characteristics', 'content'))})

    def delete(self, item_id):
        abort_if_item_not_found(item_id)
        session = db_session.create_session()
        item = session.query(items.Items).get(item_id)
        session.delete(item)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('id', required=True)
parser.add_argument('title', required=True)
parser.add_argument('price', required=True)
parser.add_argument('main_characteristics', required=True)
parser.add_argument('content', required=True)
parser.add_argument('count', required=True, type=int)


class ItemListResource(Resource):
    def get(self):
        session = db_session.create_session()
        item = session.query(items.Items).all()
        return jsonify({'item': [item_s.to_dict(
            only=('title', 'content')) for item_s in item]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        item = items.Items(
            id=args['id'],
            title=args['title'],
            price=args['price'],
            main_characteristics=args['main_characteristics'],
            content=args['content'],
            count=args['count']
        )
        session.add(item)
        session.commit()
        return jsonify({'success': 'OK'})
