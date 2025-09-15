# app_factory/create_app.py

from flask import Flask, jsonify
import werkzeug
from infrastructure.db.init_db import init_db
from config import Settings
from infrastructure.logging.logging_config import setup_logging
from routes.api import api

def create_app():
    setup_logging()
    settings = Settings()

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_string
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 1️⃣ Bind DB
    init_db(app)

    # 2️⃣ Import all models here (critical!)
    import models  # Alembic sees them

    # 3️⃣ Register blueprints
    app.register_blueprint(api, url_prefix="/api")

    # 4️⃣ HTTP error handler
    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def handle_http_exception(e):
        return jsonify({"error": e.description}), e.code

    return app