from typing import List
from sqlmodel import create_engine, Session, select
from fastapi import APIRouter, Depends, HTTPException, APIRouter
from core.models import Order
from core.database import get_session


# Initialize router
router = APIRouter(prefix="/orders", tags=["Orders"])


# 1. Create Order
@router.post("/", response_model=Order)
async def create_order(
    order: Order,
    session: Session = Depends(get_session),
):
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


# 2. Get Order by Number
@router.get("/{order_number}", response_model=Order)
async def get_order(
    order_number: int,
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# 3. Get all Orders
@router.get("/", response_model=List[Order])
async def get_all_orders(
    session: Session = Depends(get_session),
):
    orders = session.exec(select(Order)).all()
    return orders


# 4. Update Order
@router.put("/{order_number}", response_model=Order)
async def update_order(
    order_number: int,
    updated_order: Order,
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    updated_data = updated_order.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(order, key, value)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


# 5. Delete Order
@router.delete("/{order_number}")
async def delete_order(
    order_number: int,
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    session.delete(order)
    session.commit()
    return {"detail": "Order deleted successfully"}
