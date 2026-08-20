from api.controllers.auth_controller import auth_bp
from api.controllers.user_controller import user_bp
from api.controllers.dataset_controller import dataset_bp
from api.controllers.analysis_controller import analysis_bp
from api.controllers.experiment_controller import experiment_bp
from api.controllers.report_controller import report_bp
from api.controllers.audit_controller import audit_bp
from api.controllers.dashboard_controller import dashboard_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(experiment_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(dashboard_bp)
