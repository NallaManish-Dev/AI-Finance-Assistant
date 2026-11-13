from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes.auth import auth_bp
from app.routes.ai import ai_bp
from app.routes.budgets import budgets_bp
from app.routes.dashboard import dashboard_bp
from app.routes.health import health_bp
from app.routes.ml import ml_bp
from app.routes.transactions import transactions_bp
from app.services.database import register_database_commands


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    CORS(app,
    resources={
        r"/api/*": {
            "origins": app.config["CORS_ORIGINS"]
        }
    },
    supports_credentials=True)
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(ai_bp, url_prefix='/api/v1')
    app.register_blueprint(budgets_bp, url_prefix='/api/v1')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1')
    app.register_blueprint(ml_bp, url_prefix='/api/v1')
    app.register_blueprint(transactions_bp, url_prefix='/api/v1')
    register_database_commands(app)

    return app
