# infrastructure/db/init_db.py
from infrastructure.db.db_context import db

def init_db(app):
    with app.app_context():
        # Import your models here, AFTER app context is pushed
        from models.Company import Company
        # Add more models here as needed
        # db.create_all()
