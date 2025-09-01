from pydantic import BaseModel
from enum import Enum

class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class User(BaseModel):
    username: str
    email: str
    password: str
    phone_number: str | None
    balance: float

class Transaction(BaseModel):
    user_id: int
    transaction_type: TransactionType
    amount: float
    description: str | None
    reference_transaction_id: int | None
    recipient_user_id: int | None

class AddMoneyToWallet(BaseModel):
    user_id: int
    amount: float


class WithdrawMoneyFromWallet(BaseModel):
    user_id: int
    amount: float


class Transfer(BaseModel):
    transfer_id: str
    sender_user_id: int
    recipient_user_id: int
    amount: float
    description: str | None
    status: str
    created_at: str
