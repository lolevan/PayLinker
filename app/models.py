from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.utils import hash_password

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    password = Column(String, nullable=False)
    is_admin = Column(Integer, default=0)
    accounts = relationship('Account', back_populates='user')
    transactions = relationship('Transaction', back_populates='user')

    def set_password(self, password):
        self.password = hash_password(password)


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='accounts')


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    account = relationship('Account', back_populates='transactions')
    user = relationship('User', back_populates='transactions')
