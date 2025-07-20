from infrastructure.db.db_context import db
import uuid
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_processed = db.Column(db.Boolean, default=False)

    sender_id = db.Column(db.String(36), db.ForeignKey('company.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('company.id'), nullable=False)

    sender = db.relationship('Company', foreign_keys=[sender_id], backref='sent_transactions')
    receiver = db.relationship('Company', foreign_keys=[receiver_id], backref='received_transactions')
