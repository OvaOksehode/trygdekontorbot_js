# infrastructure/db/init_db.py
from flask_migrate import Migrate
from infrastructure.db.db import db
from config import settings

def init_db(app):
    db.init_app(app)

    # Init migrations explicitly
    if settings.environment == "testing":
        Migrate(app, db, render_as_batch=True)
    else:
        Migrate(app, db)