from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from schema import AuthSchema

# Create a Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# initialize AuthSchema
auth_schema = AuthSchema()


# User registration
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        auth_data = auth_schema.load(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # Return error message if validation fails

    password_hash = generate_password_hash(auth_data['password'])

    if User.query.filter_by(username=auth_data['username']).first():
        return jsonify({'error': 'User name already taken'}), 400
    if User.query.filter_by(email=auth_data['email']).first():
        return jsonify({'error': 'email already used for another account'}), 400
    new_user = User(username=auth_data['username'], password_hash=password_hash, email=auth_data['email'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# User login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        login_data = auth_schema.load(data, partial=("email",))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    user = User.query.filter_by(username=login_data['username']).first()

    if not user or not check_password_hash(user.password_hash, login_data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200
