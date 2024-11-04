from typing import List, Generator
from sqlmodel import Session, select
from fastapi import FastAPI, Depends, HTTPException
from core.models import Office
from core.database import get_session

# Initialize FastAPI router
router = FastAPI(prefix="/offices", tags=["Offices"])


# 1. Create Office
@router.post("/", response_model=Office)
async def create_office(office: Office, session: Session = Depends(get_session)):
    session.add(office)
    session.commit()
    session.refresh(office)
    return office


# 2. Get Office by Code
@router.get("/{office_code}", response_model=Office)
async def get_office(office_code: str, session: Session = Depends(get_session)):
    office = session.get(Office, office_code)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    return office


# 3. Get all Offices
@router.get("/", response_model=List[Office])
async def get_all_offices(session: Session = Depends(get_session)):
    offices = session.exec(select(Office)).all()
    return offices


# 4. Update Office
@router.put("/{office_code}", response_model=Office)
async def update_office(
    office_code: str, updated_office: Office, session: Session = Depends(get_session)
):
    office = session.get(Office, office_code)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    updated_data = updated_office.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(office, key, value)
    session.add(office)
    session.commit()
    session.refresh(office)
    return office


# 5. Delete Office
@router.delete("/{office_code}")
async def delete_office(office_code: str, session: Session = Depends(get_session)):
    office = session.get(Office, office_code)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    session.delete(office)
    session.commit()
    return {"detail": "Office deleted successfully"}
