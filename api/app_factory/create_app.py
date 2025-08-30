# app_factory/create_app.py

from flask import Flask, jsonify
import werkzeug
from infrastructure.db.init_db import init_db
from config import Settings
from infrastructure.db.db import db
from infrastructure.logging.logging_config import setup_logging
from routes.api import api

def create_app():

    setup_logging()
    settings = Settings()

    # Init Flask
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_string
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    init_db(app)

    # Register blueprints directly
    from routes.api import api
    app.register_blueprint(api, url_prefix="/api")

    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def handle_http_exception(e):
        # catches all 4xx (and any HTTPException)
        return jsonify({"error": e.description}), e.code

    return app