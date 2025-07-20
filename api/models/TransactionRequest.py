from infrastructure.db.db_context import db
import uuid
from datetime import datetime

class TransactionRequest(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = db.Column(db.String(36), db.ForeignKey('transaction.id'), nullable=False)

    sender_id = db.Column(db.String(36), db.ForeignKey('company.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('company.id'), nullable=False)

    sender = db.relationship('Company', foreign_keys=[sender_id], backref='sent_transactions')
    receiver = db.relationship('Company', foreign_keys=[receiver_id], backref='received_transactions')
    transaction = db.relationship('Transaction', backref='transaction_requests')
