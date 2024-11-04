from sqlmodel import Session, select
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from core.models import Customer
from core.database import get_session


# Initialize FastAPI router
router = APIRouter(prefix="/customers", tags=["Customer"])


# 1. Create Customer
@router.post("/", response_model=Customer, tags=["Customer"])
async def create_customer(customer: Customer, session: Session = Depends(get_session)):
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


# 2. Get Customer by Number
@router.get(
    "/{customer_number}",
    response_model=Customer,
    tags=["Customer"],
)
async def get_customer(customer_number: int, session: Session = Depends(get_session)):
    customer = session.get(Customer, customer_number)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


# 3. Get all Customer
@router.get("/", response_model=List[Customer], tags=["Customer"])
async def get_all_customers(session: Session = Depends(get_session)):
    customers = session.exec(select(Customer)).all()
    return customers


# 4. Update Customer
@router.put("/{customer_number}", response_model=Customer, tags=["Customer"])
async def update_customer(
    customer_number: int,
    updated_customer: Customer,
    session: Session = Depends(get_session),
):
    customer = session.get(Customer, customer_number)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    updated_data = updated_customer.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(customer, key, value)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


# 5. Delete Customer
@router.delete("/{customer_number}", tags=["Customer"])
async def delete_customer(
    customer_number: int, session: Session = Depends(get_session)
):
    customer = session.get(Customer, customer_number)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    session.delete(customer)
    session.commit()
    session.refresh(customer)
    return customer
