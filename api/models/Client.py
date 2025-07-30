from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from infrastructure.db.db_context import db

class Client(db.Model):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    secret = Column(String, nullable=False)
    claims = relationship("Claim", secondary="client_claim", back_populates="clients")