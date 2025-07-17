from flask_login import UserMixin
from app import db, login_manager
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Business(db.Model):
    __tablename__ = 'businesses'
    id = Column(Integer, primary_key=True)
    business_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    gst_number = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Add relationships if needed

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100))
    role = Column(String(10), nullable=False, default='staff')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    business_id = Column(Integer, db.ForeignKey('businesses.id'))
    business = relationship('Business', backref='users')

    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 