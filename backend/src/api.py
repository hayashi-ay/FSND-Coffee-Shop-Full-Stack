import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
@app.route('/drinks')
def get_drinks():
    drinks = list(map(lambda  x: x.short(), Drink.query.all() ) )
    return jsonify( {"success": True, "drinks": drinks} ), 200

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = list(map(lambda  x: x.long(), Drink.query.all() ) )
    return jsonify( { "success": True, "drinks": drinks } ), 200

@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drinks(jwt):
    body = request.get_json()
    drink = Drink( body['title'], json.dumps(body['recipe']) )

    drink.insert()
    return jsonify( { "success": True, "drinks": drink.long() } ), 200

@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drinks(jwt, drink_id):
    body = request.get_json()

    if drink_id is None:
        abort(404, "resource not found")

    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if drink is None:
        abort(404, "resource not found")

    drink.title = body['title']
    drink.recipe = json.dumps(body['recipe'])

    drink.update()
    return jsonify( { "success": True, "drinks": drink.long() } ), 200

@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):
    if drink_id is None:
        abort(404, "resource not found")

    Drink.query.get(drink_id).delete()
    return jsonify( { "success": True, "delete": drink_id } ), 200

## Error Handling
@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(422)
def errorhandler(error):
    return jsonify({
        "success": False,
        "error": error.code,
        "message": error.description
    }, error.code)