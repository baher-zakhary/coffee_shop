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
@ uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@ implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/api/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "drinks": list(map(lambda drink: drink.short(), drinks))
    })


'''
@ implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/api/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    return jsonify({
        "success": True,
        "drinks": list(map(lambda drink: drink.long(), drinks))
    })

'''
@ implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/api/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    body = request.get_json()
    try:
        title = body.get('title', None)
        recipe = json.dumps(body.get('recipe', None))
    except Exception:
        abort(422)
    if title is None or recipe is None:
        abort(400)
    try:
        new_drink = Drink(title = title, recipe = recipe)
        new_drink.insert()
    except:
        abort(422)
    new_drink = Drink.query.filter(Drink.title == new_drink.title).first()
    return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
            })
'''
@ implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/api/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id):
    drink = Drink.query.filter(Drink.id == id).first()
    if drink is None:
        abort(404)
    try:
        body = request.get_json()
        title = body.get('title', None)
        if title is not None:
            drink.title = title
        recipe = json.dumps(body.get('recipe', None))
        if recipe is not None:
            drink.recipe = recipe
        drink.update()
    except:
        abort(422)
    return jsonify({
            "success": True,
            "drinks": [drink.long()]
            })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    message = "unprocessable"
    if error.description:
        message = error.description
    return jsonify({
            "success": False, 
            "error": 422,
            "message": message
            }), 422

'''
@ implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@ implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    message = "resource not found"
    if error.description:
        message = error.description
    return jsonify({
            "success": False,
            "error": 404,
            "message": message
        }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def unauthorized(error):
    message = "Unauthorized"
    if error.description:
        message = error.description
    return jsonify({
        "success": False,
        "error": 401,
        "message": message
    }), 401

@app.errorhandler(403)
def unauthorized(error):
    message = "Forbidden"
    if error.description:
        message = error.description
    return jsonify({
        "success": False,
        "error": 403,
        "message": message
    }), 403

@app.errorhandler(400)
def bad_request(error):
    message = "Bad request"
    if error.description:
        message = error.description
    return jsonify({
        "success": False,
        "error": 400,
        "message": message
    }), 400

@app.errorhandler(500)
def unauthorized(error):
    message = "Internal server error"
    if error.description:
        message = error.description
    return jsonify({
        "success": False,
        "error": 500,
        "message": message
    }), 500