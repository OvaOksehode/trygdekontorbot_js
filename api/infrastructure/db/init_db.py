# infrastructure/db/init_db.py
from flask_migrate import Migrate, upgrade
from infrastructure.db.db import db
from config import settings

def init_db(app):
    db.init_app(app)
        
    # Init migrations explicitly
    if settings.environment == "testing":
        with app.app_context():
            db.create_all()
    else:
        Migrate(app, db)