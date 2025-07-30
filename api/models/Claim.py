from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from infrastructure.db.db_context import db

class Claim(db.Model):
    __tablename__ = "claim"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    clients = relationship("Client", secondary="client_claim", back_populates="claims")