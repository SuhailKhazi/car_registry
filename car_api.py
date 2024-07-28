#%%
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import datetime
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__)

CORS(app)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin@localhost/cars_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Car Model
class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    vin = db.Column(db.String(50), nullable = False)
    ShippingStatus = db.Column(db.String(20), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Login for JWT token
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    # Example: authenticate username and password
    if username == 'admin' and password == 'password':
        token = create_access_token(identity=username)
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# Get Cars endpoint
@app.route('/cars', methods=['GET'])
@jwt_required()
def get_cars():
    make = request.args.get('make')
    model = request.args.get('model')
    year = request.args.get('year')
    VIN = request.args.get('VIN')
    ShippingStatus = request.args.get('ShippingStatus')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    query = Car.query
    if make:
        query = query.filter_by(make=make)
    if model:
        query = query.filter_by(model=model)
    if year:
        query = query.filter_by(year=year)
    if VIN:
        query = query.filter_by(VIN = VIN)
    if ShippingStatus:
        query = query.filter_by(ShippingStatus=ShippingStatus)

    # cars_paginated = query.paginate(page, per_page, False)
    cars_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    cars_list = [{
        'id': car.id,
        'make': car.make,
        'model': car.model,
        'year': car.year,
        'VIN': car.vin,
        'ShippingStatus': car.ShippingStatus
    } for car in cars_paginated.items]

    return jsonify(cars_list)

# Add Car endpoint
@app.route('/cars', methods=['POST'])
@jwt_required()
def add_car():
    data = request.get_json()
    print("data: ",data)
    if not all(k in data for k in ('make', 'model', 'year','VIN', 'ShippingStatus')):
        return jsonify({'message': 'Missing fields'}), 400

    new_car = Car(
        make=data['make'],
        model=data['model'],
        year=data['year'],
        VIN = data['VIN'],
        ShippingStatus=data['ShippingStatus']
    )
    db.session.add(new_car)
    db.session.commit()
    return jsonify({'id': new_car.id}), 201

# Update Status endpoint
@app.route('/cars/<int:car_id>', methods=['PATCH'])
@jwt_required()
def update_status(car_id):
    data = request.get_json()
    if 'ShippingStatus' not in data:
        return jsonify({'message': 'Missing ShippingStatus field'}), 400

    car = Car.query.get(car_id)
    if car:
        car.ShippingStatus = data['ShippingStatus']
        db.session.commit()
        return jsonify({'id': car.id, 'ShippingStatus': car.ShippingStatus})
    return jsonify({'message': 'Car not found'}), 404

# Delete Car endpoint
@app.route('/cars/<int:car_id>', methods=['DELETE'])
@jwt_required()
def delete_car(car_id):
    car = Car.query.get(car_id)
    if car:
        db.session.delete(car)
        db.session.commit()
        return jsonify({'message': 'Car deleted'}), 204
    return jsonify({'message': 'Car not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
