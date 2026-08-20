from marshmallow import Schema, fields, validate


class UserResponseSchema(Schema):
    user_id = fields.Int()
    full_name = fields.Str()
    email = fields.Str()
    role = fields.Str()
    created_at = fields.DateTime()


class CreateUserRequestSchema(Schema):
    full_name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(required=True, validate=validate.OneOf(
        ["admin", "researcher", "analyst", "student"]))
