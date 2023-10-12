from flask import Flask, request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')

@app.route('/')
def default_hi():
    print("Hi, there!")
    return "Hi, there from earth!" 


@app.route('/<name>')
def print_hi(name):
    print(f'Hi, {name}')
    return f'Hi, {name}'


@app.route('/not_found')
def not_fount():
    return jsonify(message="That response was not found"), 404


@app.route('/super_simple')
def super_simple():
    print("Hello From The Moon")
    return jsonify(message= "Hello From The Moon API"), 200


@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name:str, age:int):
    if age < 18:
        return jsonify(message= " Sorry " + name + " You are not old enough "), 401
    else:
        return jsonify(message= "We meet again " + name)


@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message= " Sorry " + name + " You are not old enough "), 401
    else:
        return jsonify(message= "We meet again " + name)
    


if __name__ == '__main__':
    app.run(debug=True)
