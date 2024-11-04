from typing import List, Generator
from sqlmodel import Relationship, Session, select
from fastapi import APIRouter, Depends, HTTPException
from core.models import ProductLine, Product
from core.database import get_session

# Initialize FastAPI router
router = APIRouter(prefix="/products", tags=["Product"])


# 6. Create Product
@router.post("/", response_model=Product)
async def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


# 7. Get Product by Code
@router.get("/{product_code}", response_model=Product)
async def get_product(product_code: str, session: Session = Depends(get_session)):
    product = session.get(Product, product_code)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# 8. Get all Products with ProductLine details
@router.get("/", response_model=List[Product])
async def get_all_products(session: Session = Depends(get_session)):
    products = session.exec(
        select(Product).options(Relationship("productLine_relation"))
    ).all()
    return products


# 9. Update Product
@router.put("/{product_code}", response_model=Product)
async def update_product(
    product_code: str, updated_product: Product, session: Session = Depends(get_session)
):
    product = session.get(Product, product_code)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    updated_data = updated_product.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(product, key, value)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


# 10. Delete Product
@router.delete("/{product_code}")
async def delete_product(product_code: str, session: Session = Depends(get_session)):
    product = session.get(Product, product_code)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()
    return {"detail": "Product deleted successfully"}
