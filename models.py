from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(15))
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One user can have many transactions
    transactions = relationship("Transaction", foreign_keys="Transaction.user_id", back_populates="user")
    
    # One user can receive many transactions
    received_transactions = relationship("Transaction", foreign_keys="Transaction.recipient_user_id", back_populates="recipient")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    transaction_type = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text)

    reference_transaction_id = Column(Integer, ForeignKey("transactions.id"))
    recipient_user_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Many transactions belong to one user (the sender)
    user = relationship("User", foreign_keys=[user_id], back_populates="transactions")
    
    # Many transactions can have one recipient user
    recipient = relationship("User", foreign_keys=[recipient_user_id], back_populates="received_transactions")
    
    # Self-referential relationship for reference transactions
    reference_transaction = relationship("Transaction", remote_side=[id])



