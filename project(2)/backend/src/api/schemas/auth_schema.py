from marshmallow import Schema, fields, validate


class RegisterRequestSchema(Schema):
    full_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(load_default="student",
                       validate=validate.OneOf(["admin", "researcher", "analyst", "student"]))


class LoginRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class ChangePasswordRequestSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
