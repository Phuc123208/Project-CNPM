from marshmallow import Schema, fields


class DatasetResponseSchema(Schema):
    dataset_id = fields.Int()
    user_id = fields.Int()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime()


class DatasetVersionResponseSchema(Schema):
    version_id = fields.Int()
    dataset_id = fields.Int()
    version_number = fields.Str()
    row_count = fields.Int()
    start_time = fields.DateTime(allow_none=True)
    end_time = fields.DateTime(allow_none=True)
    validation_report = fields.Dict(allow_none=True)
    created_at = fields.DateTime()
