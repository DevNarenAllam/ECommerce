from typing import List
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from core.models import ProductLine
from core.database import get_session

# Initialize FastAPI router
router = APIRouter(prefix="/productlines", tags=["ProductLine"])


# 1. Create ProductLine
@router.post("/", response_model=ProductLine)
async def create_product_line(
    product_line: ProductLine, session: Session = Depends(get_session)
):
    session.add(product_line)
    session.commit()
    session.refresh(product_line)
    return product_line


# 2. Get ProductLine by ID
@router.get("/{product_line_id}", response_model=ProductLine)
async def get_product_line(
    product_line_id: str, session: Session = Depends(get_session)
):
    product_line = session.get(ProductLine, product_line_id)
    if not product_line:
        raise HTTPException(status_code=404, detail="ProductLine not found")
    return product_line


# 3. Get all ProductLines
@router.get("/", response_model=List[ProductLine])
async def get_all_product_lines(session: Session = Depends(get_session)):
    product_lines = session.exec(select(ProductLine)).all()
    return product_lines


# 4. Update ProductLine
@router.put("/{product_line_id}", response_model=ProductLine)
async def update_product_line(
    product_line_id: str,
    updated_product_line: ProductLine,
    session: Session = Depends(get_session),
):
    product_line = session.get(ProductLine, product_line_id)
    if not product_line:
        raise HTTPException(status_code=404, detail="ProductLine not found")
    updated_data = updated_product_line.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(product_line, key, value)
    session.add(product_line)
    session.commit()
    session.refresh(product_line)
    return product_line


# 5. Delete ProductLine
@router.delete("/{product_line_id}")
async def delete_product_line(
    product_line_id: str, session: Session = Depends(get_session)
):
    product_line = session.get(ProductLine, product_line_id)
    if not product_line:
        raise HTTPException(status_code=404, detail="ProductLine not found")
    session.delete(product_line)
    session.commit()
    return {"detail": "ProductLine deleted successfully"}
