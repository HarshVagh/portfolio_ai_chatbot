from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db, bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    Migrate(app, db)

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.chat_routes import chat_bp
    from app.routes.deploy_routes import deploy_bp
    from app.routes.message_routes import message_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(deploy_bp)
    app.register_blueprint(message_bp)

    return app
