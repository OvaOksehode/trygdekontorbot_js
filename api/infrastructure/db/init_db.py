# infrastructure/db/init_db.py
from flask_migrate import Migrate
from infrastructure.db.db import db

def init_db(app):
    db.init_app(app)
    # Make sure DB schema is created (instead of init_db wrapper)
    with app.app_context():
        db.create_all()
    # Init migrations explicitly
    Migrate(app, db)