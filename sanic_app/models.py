
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    bank_accounts = relationship("BankAccount", back_populates="user")
    is_admin = Column(Boolean, nullable=False, default=False)


class BankAccount(Base):
    __tablename__ = 'bank_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    balance = Column(Integer, nullable=False, default=0)
    orders = relationship("Order", back_populates="bank_account")
    user = relationship("User", back_populates="bank_accounts")


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(50), nullable=False, unique=True)
    amount = Column(Integer, nullable=False)
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    datetime = Column(DateTime, nullable=False, default=datetime.now)
    bank_account = relationship("BankAccount", back_populates="orders")

if __name__ == '__main__':
    from connection import DBConnection
    conn = DBConnection()

    Base.metadata.create_all(
        bind=conn.engine,
    )
