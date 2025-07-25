# app_factory/create_app.py

from flask import Flask
from config import Settings
from infrastructure.db.db_context import db, init_app
from infrastructure.db.init_db import init_db
from infrastructure.logging.logging_config import setup_logging
from routes.api import api

def create_app():
    setup_logging()
    settings = Settings()
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_string

    init_app(app)
    init_db(app)

    from models import Company  # Delay to avoid circular import
    with app.app_context():
        db.create_all()

    app.register_blueprint(api, url_prefix="/api")
    return app
