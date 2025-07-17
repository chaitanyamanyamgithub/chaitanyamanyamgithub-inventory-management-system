from app import db
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

class CompanyInfo(db.Model):
    __tablename__ = 'company_info'
    id = Column(Integer, primary_key=True, default=1)
    company_name = Column(String(100), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(100))
    tax_id = Column(String(50))
    logo_path = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 