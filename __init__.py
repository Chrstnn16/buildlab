from flask import Flask
from database.db import db
from routes.auth_routes import auth_bp
from routes.build_routes import build_bp
from routes.component_routes import component_bp
from routes.admin_routes import admin_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "buildlab-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/users.db"
    app.config["SQLALCHEMY_BINDS"] = {
        "components": "sqlite:///instance/components.db"
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(build_bp)
    app.register_blueprint(component_bp)
    app.register_blueprint(admin_bp)

    return app
