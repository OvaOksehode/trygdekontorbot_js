from infrastructure.db.db_context import db
import uuid

class Company(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    experience_in_years = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)

    last_trygd_claim = db.Column(db.Integer, nullable=False)
    trygd_amount = db.Column(db.Integer, nullable=False)
