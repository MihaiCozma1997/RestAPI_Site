from marshmallow import Schema, fields, ValidationError
import re


def validate_username(value):
    # Ensure the username is at least 3 characters long
    if len(value) < 3:
        raise ValidationError("Username must be at least 3 characters long.")

    # Ensure the username only contains alphanumeric characters (no spaces, symbols, etc.)
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        raise ValidationError("Username must only contain letters and numbers.")


def must_be_positive(value):
    if value <= 0:
        raise ValidationError("Price must be greater than zero.")


def rating_validation(value):
    if value <= 0 or value > 5:
        raise ValidationError("Rating should be between 1 and 5")


def password_validation(value):
    if len(value) < 8:
        raise ValidationError("Password should have at least 8 char")


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True, validate=must_be_positive)
    description = fields.Str(required=False, allow_none=True)


class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    rating = fields.Int(required=True, validate=rating_validation)
    comment = fields.Str(required=False)
    product_id = fields.Int(dump_only=True)
    user_name = fields.Str(dump_only=True)


class AuthSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate_username)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=password_validation)
