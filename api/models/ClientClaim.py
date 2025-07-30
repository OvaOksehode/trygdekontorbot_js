from sqlalchemy import Column, Integer, ForeignKey
from infrastructure.db.db_context import db

class ClientClaim(db.Model):
    __tablename__ = "client_claim"
    client_id = Column(Integer, ForeignKey("client.id"), primary_key=True)
    claim_id = Column(Integer, ForeignKey("claim.id"), primary_key=True)