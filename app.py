# app.py
from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from schema import ProductSchema, ReviewSchema
import os
from auth import auth_bp  # Import your blueprint

jwt = JWTManager()
product_schema = ProductSchema(exclude=['id'])
products_schema = ProductSchema(many=True)
review_schema = ReviewSchema(exclude=['id', 'product_id'])
reviews_schema = ReviewSchema(many=True, exclude=['id', 'product_id'])


def create_app(test_config=None):
    app = Flask(__name__, static_folder="static")

    if test_config:
        app.config.update(test_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev')  # fallback for testing

    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints/routes
    from routes import register_routes
    register_routes(app)
    app.register_blueprint(auth_bp, url_prefix='/auth')  # ✅ Register auth routes

    return app
