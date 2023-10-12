from flask import Flask, request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from Models import database_models

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')

@app.route('/')
def default_hi():
    print("Hi, there!")
    return "Hi, there from earth!" 

# Configure our database 
db = SQLAlchemy(app)

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('database Created!')



@app.cli.command('db_drop')
def fb_drop():
    db.drop_all()
    print('Database Dropped!')


@app.cli.command('db_seed')
def db_seed():
    mercury = database_models.Planet(planet_name = 'Mercury',
                                     planet_type = 'Class D',
                                     home_star='Sol',
                                     mass=3.258e23,
                                     radius=1516,
                                     distance=35.98e6)
    
    venus = database_models.Planet(planet_name = 'Venus',
                                     planet_type = 'Class k',
                                     home_star='Sol',
                                     mass=4.867e24,
                                     radius=3760,
                                     distance=67.24e6)
    
    earth = database_models.Planet(planet_name = 'Earth',
                                     planet_type = 'Class M',
                                     home_star='Sol',
                                     mass=5.972e24,
                                     radius=3959,
                                     distance=92.96e6)
    
    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = database_models.User(first_name='William',
                                     last_name='Herschel',
                                     email='test@test.com',
                                     password='P@ssw0rd')
    
    db.session.add(test_user)
    # Commit needed to save session
    db.session.commit() 
    print('Database seeded!')

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

