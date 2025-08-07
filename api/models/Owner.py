from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from infrastructure.db.db_context import db

class Owner(db.Model):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    highest_balance = Column(Integer, nullable=False, default=0)