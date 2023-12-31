from flask import Flask, request, send_file
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
from flask_restful import Api
from PIL import Image  



app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret' #change IRL 
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '61588f4603c5e3'
app.config['MAIL_PASSWORD'] = '539a7fd1ac64af'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
# Configure our database 
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)
api= Api(app)


@app.route('/')
def default_hi():
    print("Hi, there!")
    return "Hi, there from earth!" 

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
    mercury = Planet(planet_name='Mercury',
                     planet_type='Class D',
                     home_star='Sol',
                     mass=2.258e23,
                     radius=1516,
                     distance=35.98e6)

    venus = Planet(planet_name='Venus',
                         planet_type='Class K',
                         home_star='Sol',
                         mass=4.867e24,
                         radius=3760,
                         distance=67.24e6)

    earth = Planet(planet_name='Earth',
                     planet_type='Class M',
                     home_star='Sol',
                     mass=5.972e24,
                     radius=3959,
                     distance=92.96e6)

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='William',
                     last_name='Herschel',
                     email='test@test.com',
                     password='P@ssw0rd')

    db.session.add(test_user)
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


@app.route('/planet_image')
def planet_image(request):
    print(request)
    image=request.FILES['image']
    return jsonify(message= "Image Recieved"), 200


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
    

@app.route('/planets', methods= ['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)

@app.route('/register', methods=['POST'])
def register():

    email = request.args.get('email')
   
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists.'), 409
    else:
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        password = request.args.get('password')
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully."), 201
    # Supporting a pure json post 


@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']
    if file:
        file.save(file.filename)
        # return send_file("102820308_C72_1.jpeg", mimetype='image/jpg')
        return {"message": "Image uploaded successfully"}, 200
    else:
        return {"message": "No file provided"}, 400



@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        # This is going to be useful for mobile applications 
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.args.get('email')
        password = request.args.get('password')
        
    # Check to see if there's a match
    # We can look for the first since it's illegal to have two of the same identifiers 
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="login succeeded", access_token=access_token)
    else:
        return jsonify(message="You enetered a bad email or password"), 401
    
    
@app.route('/retrive_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("Your planetery api password is" + user.password,
                      sender="Admin@planetary-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message= "Password sent to " + email)
    else:
        return jsonify(message= "That email doesn't")
    
    
@app.route('/planet_details/<int:planet_id>', methods=["GET"])
def planet_details(planet_id: int):
    planet  = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="That planet deos not exsist"), 404

@jwt_required()
@app.route('/add_planet', methods=['POST'])
def add_planet():
    planet_name = request.args.get('planet_name')
    
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify("There is already a planet by that name"), 409
    else:
        
        planet_type = request.args.get('planet_type')
        home_star = request.args.get('home_star')
        mass = float(request.args.get('mass'))
        radius = float(request.args.get('radius'))
        distance = float(request.args.get('distance'))
        
        
        
        new_planet = Planet(planet_name=planet_name,
                            planet_type=planet_type,
                            home_star=home_star,
                            mass=mass,
                            radius=radius,
                            distance=distance)
        
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message="You added a planet"), 201
    
@jwt_required()
@app.route('/update_planet', methods=['PUT'])
def update_planet():
    planet_id = int(request.args.get('planet_id'))
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.args.get('planet_name')
        planet.planet_type = request.args.get('planet_type')
        planet.home_star = request.args.get('home_star')
        planet.mass = float(request.args.get('mass'))
        planet.radius = float(request.args.get('radius'))
        planet.distance = float(request.args.get('distance'))
        db.session.commit()
        return jsonify(message="Yup you updated a planet"), 202
    else:
        return jsonify(message="The planet does not exist")

@jwt_required()
@app.route('/remove_planet/<int:planet_id>', methods=['DELETE'])
def remove_planet(planet_id:int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message= "Yup you deleted a planet there MR planetory destroyer"), 202
    else:
        return jsonify(messgae= "That planet does not exist")

# database models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


# tell marshmallow which fields its looking for

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta: 
        fields = ('planet_id', 'planet_name', 'planet_type',
                  'home_star', 'mass', 'radius', 'distance')
        
user_schema = UserSchema()
# deserliaze multple records back 
users_schema = UserSchema(many=True)
planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)




if __name__ == '__main__':
    app.run(debug=True)
