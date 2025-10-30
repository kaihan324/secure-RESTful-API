from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    key = relationship('UserKey', back_populates='user', uselist=False)

class UserKey(Base):
    __tablename__ = 'user_keys'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    encrypted_key = Column(LargeBinary, nullable=False)
    user = relationship('User', back_populates='key')

class SensitiveData(Base):
    __tablename__ = 'sensitive_data'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    data = Column(LargeBinary, nullable=False)
    description = Column(String, nullable=True)
