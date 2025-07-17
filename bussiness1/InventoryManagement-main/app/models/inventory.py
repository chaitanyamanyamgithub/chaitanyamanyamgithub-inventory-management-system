from app import db
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey
from datetime import datetime

class StockAdjustment(db.Model):
    __tablename__ = 'stock_adjustments'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    adjustment_date = Column(DateTime, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 