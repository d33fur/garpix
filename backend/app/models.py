from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base

class Standart(Base):
    __tablename__ = "standarts"
    id = Column(Integer, primary_key=True, index=True)
    standart_name = Column(String, index=True, unique=True, nullable=False)
    standart_json = Column(JSONB, nullable=False)
