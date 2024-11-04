from typing import List
from sqlmodel import create_engine, Session, select
from fastapi import Depends, HTTPException, APIRouter
from core.models import OrderDetail
from core.database import get_session


# Initialize  router
router = APIRouter(prefix="/orderdetails", tags=["OrderDetails"])


# 6. Create OrderDetail
@router.post("/", response_model=OrderDetail)
async def create_order_detail(
    order_detail: OrderDetail,
    session: Session = Depends(get_session),
):
    session.add(order_detail)
    session.commit()
    session.refresh(order_detail)
    return order_detail


# 7. Get OrderDetail by Order Number and Product Code
@router.get("/{order_number}/{product_code}", response_model=OrderDetail)
async def get_order_detail(
    order_number: int,
    product_code: str,
    session: Session = Depends(get_session),
):
    statement = select(OrderDetail).where(
        OrderDetail.orderNumber == order_number, OrderDetail.productCode == product_code
    )
    order_detail = session.exec(statement).first()
    if not order_detail:
        raise HTTPException(status_code=404, detail="OrderDetail not found")
    return order_detail


# 8. Get all OrderDetails
@router.get("/", response_model=List[OrderDetail])
async def get_all_order_details(
    session: Session = Depends(get_session),
):
    order_details = session.exec(select(OrderDetail)).all()
    return order_details


# 9. Update OrderDetail
@router.put("/{order_number}/{product_code}", response_model=OrderDetail)
async def update_order_detail(
    order_number: int,
    product_code: str,
    updated_order_detail: OrderDetail,
    session: Session = Depends(get_session),
):
    statement = select(OrderDetail).where(
        OrderDetail.orderNumber == order_number, OrderDetail.productCode == product_code
    )
    order_detail = session.exec(statement).first()
    if not order_detail:
        raise HTTPException(status_code=404, detail="OrderDetail not found")
    updated_data = updated_order_detail.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(order_detail, key, value)
    session.add(order_detail)
    session.commit()
    session.refresh(order_detail)
    return order_detail


# 10. Delete OrderDetail
@router.delete("/{order_number}/{product_code}")
async def delete_order_detail(
    order_number: int,
    product_code: str,
    session: Session = Depends(get_session),
):
    statement = select(OrderDetail).where(
        OrderDetail.orderNumber == order_number, OrderDetail.productCode == product_code
    )
    order_detail = session.exec(statement).first()
    if not order_detail:
        raise HTTPException(status_code=404, detail="OrderDetail not found")
    session.delete(order_detail)
    session.commit()
    return {"detail": "OrderDetail deleted successfully"}
