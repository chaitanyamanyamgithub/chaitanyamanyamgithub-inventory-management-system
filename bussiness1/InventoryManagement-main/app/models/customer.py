from app import db
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    business_id = Column(Integer, db.ForeignKey('businesses.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 