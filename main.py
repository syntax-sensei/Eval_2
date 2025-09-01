from fastapi import FastAPI, Depends
from models import User as UserModel, Transaction as TransactionModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from schemas import User as UserSchema, Transaction as TransactionSchema, AddMoneyToWallet, WithdrawMoneyFromWallet, Transfer as TransferSchema, TransactionType

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

def generate_id(db: Session):
    last_entry = db.query(UserModel).order_by(UserModel.id.desc()).first()
    if last_entry:
        return last_entry.id + 1
    return 1

def generate_transaction_id(db: Session):
    last_entry = db.query(TransactionModel).order_by(TransactionModel.id.desc()).first()
    if last_entry:
        return last_entry.id + 1
    return 1

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        return user
    return {"error": "User not found"}

@app.post("/users/")
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    user_id = generate_id(db)
    db_user = UserModel(id=user_id, **user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# PUT /users/{user_id}
# Request Body:
# {
#   "username": "string",
#   "phone_number": "string"
# }
# Response: 200 OK

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        for key, value in user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    return {"error": "User not found"}

@app.get("/wallet/{user_id}/balance")
def get_wallet_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        return {"user_id": user_id, "balance": user.balance}
    return {"error": "User not found"}



@app.post("/wallet/{user_id}/add-money")
def add_money_to_wallet(user_id: int, transaction: AddMoneyToWallet, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        user.balance += transaction.amount
        db.commit()
        db.refresh(user)

        db_transaction = TransactionModel(
            user_id=user_id,
            transaction_type=TransactionType.CREDIT,
            amount=transaction.amount
        )
        db.add(db_transaction)
        db.commit()

        return {
            "transaction_id": generate_transaction_id(db),
            "user_id": user_id,
            "amount": transaction.amount,
            "new_balance": user.balance,
            "transaction_type": "CREDIT"
        }
    return {"error": "User not found"}

@app.post("/wallet/{user_id}/withdraw")
def withdraw_money_from_wallet(user_id: int, transaction: WithdrawMoneyFromWallet, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user:
        user.balance -= transaction.amount
        db.commit()
        db.refresh(user)

        db_transaction = TransactionModel(
            user_id=user_id,
            transaction_type=TransactionType.DEBIT,
            amount=transaction.amount
        )
        db.add(db_transaction)
        db.commit()

        return {
            "transaction_id": generate_transaction_id(db),
            "user_id": user_id,
            "amount": transaction.amount,
            "new_balance": user.balance,
            "transaction_type": "DEBIT"
        }
    return {"error": "User not found"}

# @app.post("/transactions")
# def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
#     db_transaction = TransactionModel(**transaction.dict())
#     db.add(db_transaction)
#     db.commit()
#     db.refresh(db_transaction)
#     return db_transaction

@app.post("/transfer")
def transfer_money(sender_user_id: int, recipient_user_id: int, amount: float, description: str | None = None, db: Session = Depends(get_db)):
    sender = db.query(UserModel).filter(UserModel.id == sender_user_id).first()
    recipient = db.query(UserModel).filter(UserModel.id == recipient_user_id).first()

    if not sender:
        return {"error": "Sender not found"}, 404
    if not recipient:
        return {"error": "Recipient not found"}, 404

    if sender.balance < amount:
        return {
            "error": "Insufficient balance",
            "current_balance": sender.balance,
            "required_amount": amount
        }, 400

    # Create transactions
    sender_transaction = TransactionModel(
        user_id=sender_user_id,
        transaction_type=TransactionType.DEBIT,
        amount=amount,
        description=description,
        recipient_user_id=recipient_user_id,
        
    )
    recipient_transaction = TransactionModel(
        user_id=recipient_user_id,
        transaction_type=TransactionType.CREDIT,
        amount=amount,
        description=description,
        recipient_user_id=recipient_user_id,
        
    )

    db.add(sender_transaction)
    db.add(recipient_transaction)
    db.commit()

    # Update balances
    sender.balance -= amount
    recipient.balance += amount
    db.commit()

    return {
        "transfer_id": "unique_transfer_id",
        "sender_transaction_id": sender_transaction.id,
        "recipient_transaction_id": recipient_transaction.id,
        "amount": amount,
        "sender_new_balance": sender.balance,
        "recipient_new_balance": recipient.balance,
        "status": "completed"
    }

# GET /transfer/{transfer_id}
# Response: 200 OK
# {
#   "transfer_id": "unique_transfer_id",
#   "sender_user_id": 1,
#   "recipient_user_id": 2,
#   "amount": 25.00,
#   "description": "Payment for dinner",
#   "status": "completed",
#   "created_at": "2024-01-01T12:30:00Z"
# }

@app.get("/transfer/{transfer_id}")
def get_transfer_details(transfer_id: str, db: Session = Depends(get_db)):
    transfer = db.query(TransactionModel).filter(TransactionModel.id == transfer_id).first()
    if not transfer:
        return {"error": "Transfer not found"}, 404
    return transfer