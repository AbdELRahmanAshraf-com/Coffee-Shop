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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ----------   ROUTES   ----------#
# GET /drinks
@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()
    li_drinks = [drink.short() for drink in drinks]
    if drinks is None or len(li_drinks) == 0:
        abort(404)
    return jsonify({"success": True, "drinks": li_drinks})


# GET /drinks-detail
@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drink_details(payload):
    drinks = Drink.query.all()
    li_drinks = [drink.long() for drink in drinks]
    if drinks is None or len(li_drinks) == 0:
        abort(404)
    return jsonify({"success": True, "drinks": li_drinks}), 200


# POST /drinks
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(payload):
    req = request.get_json()
    title = req.get('title')
    recipe = req.get('recipe')
    if title and recipe:
        try:
            drink = Drink(title=title, recipe=json.dumps(recipe))
            drink.insert()
        except:
            abort(400)
        return jsonify({"success": True, "drinks": [drink.long()]})
    else:
        abort(400)

# PATCH /drinks/<int:id>


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def edit_drink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    try:
        req = request.get_json()
        title = req.get('title')
        recipe = json.dumps(req.get('recipe'))
        if title and recipe:
            drink.title = title
            drink.recipe = recipe
            drink.update()
    except:
        abort(400)
    return jsonify({"success": True, "drinks": [drink.long()]})

# DELETE /drinks/<int:id>


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    drink.delete()
    return jsonify({"success": True, "delete": id})


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(e):
    # response = jsonify(e.error)
    # response.status_code = e.status_code
    return jsonify(e.error), e.status_code
