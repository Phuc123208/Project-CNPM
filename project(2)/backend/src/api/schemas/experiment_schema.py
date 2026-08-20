from marshmallow import Schema, fields, validate


class CreateExperimentRequestSchema(Schema):
    version_id = fields.Int(required=True)
    name = fields.Str(required=True)
    model_type = fields.Str(required=True, validate=validate.OneOf(["arima", "prophet"]))
    parameters = fields.Dict(load_default=dict)


class ExperimentResponseSchema(Schema):
    experiment_id = fields.Int()
    user_id = fields.Int()
    version_id = fields.Int()
    name = fields.Str()
    model_type = fields.Str()
    parameters = fields.Dict()
    evaluation_metrics = fields.Dict()
    status = fields.Str()
    created_at = fields.DateTime()
