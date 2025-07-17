from app import db
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = (db.UniqueConstraint('name', 'business_id', name='uq_category_name_business'),)
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False)
    # Relationship to products
    products = relationship('Product', backref='category')

class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    current_stock = Column(Numeric(10, 2), default=0)
    min_stock_level = Column(Numeric(10, 2), default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add business relationship if needed 