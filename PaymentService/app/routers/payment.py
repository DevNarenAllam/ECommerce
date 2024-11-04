from typing import List, Generator
from sqlmodel import create_engine, Session, select
from fastapi import APIRouter, Depends, HTTPException
from core.models import Payment
from core import DATABASE_URL
from core.database import get_session


# Initialize FastAPI router
router = APIRouter(prefix="/payments", tags=["Payment"])


# 1. Create Payment
@router.post("/", response_model=Payment)
async def create_payment(payment: Payment, session: Session = Depends(get_session)):
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


# 2. Get Payment by Customer Number and Check Number
@router.get("/{customer_number}/{check_number}", response_model=Payment)
async def get_payment(
    customer_number: int, check_number: str, session: Session = Depends(get_session)
):
    statement = select(Payment).where(
        Payment.customerNumber == customer_number, Payment.checkNumber == check_number
    )
    payment = session.exec(statement).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


# 3. Get all Payments
@router.get("/", response_model=List[Payment])
async def get_all_payments(session: Session = Depends(get_session)):
    payments = session.exec(select(Payment)).all()
    return payments


# 4. Update Payment
@router.put("/customer_number}/{check_number}", response_model=Payment)
async def update_payment(
    customer_number: int,
    check_number: str,
    updated_payment: Payment,
    session: Session = Depends(get_session),
):
    statement = select(Payment).where(
        Payment.customerNumber == customer_number, Payment.checkNumber == check_number
    )
    payment = session.exec(statement).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    updated_data = updated_payment.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(payment, key, value)
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


# 5. Delete Payment
@router.delete("/{customer_number}/{check_number}")
async def delete_payment(
    customer_number: int, check_number: str, session: Session = Depends(get_session)
):
    statement = select(Payment).where(
        Payment.customerNumber == customer_number, Payment.checkNumber == check_number
    )
    payment = session.exec(statement).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    session.delete(payment)
    session.commit()
    return {"detail": "Payment deleted successfully"}
