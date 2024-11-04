from typing import List, Generator
from sqlmodel import create_engine, Session, select
from fastapi import APIRouter, Depends, HTTPException
from core.models import Employee
from core.config import DATABASE_URL
from core.database import get_session


# Initialize FastAPI router
router = APIRouter(prefix="/employees", tags=["Employee"])


# 1. Create Employee
@router.post("/", response_model=Employee)
async def create_employee(employee: Employee, session: Session = Depends(get_session)):
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


# 2. Get Employee by Number
@router.get("/{employee_number}", response_model=Employee)
async def get_employee(employee_number: int, session: Session = Depends(get_session)):
    employee = session.get(Employee, employee_number)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


# 3. Get all Employees
@router.get("/", response_model=List[Employee])
async def get_all_employees(session: Session = Depends(get_session)):
    employees = session.exec(select(Employee)).all()
    return employees


# 4. Update Employee
@router.put("/{employee_number}", response_model=Employee)
async def update_employee(
    employee_number: int,
    updated_employee: Employee,
    session: Session = Depends(get_session),
):
    employee = session.get(Employee, employee_number)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    updated_data = updated_employee.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(employee, key, value)
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


# 5. Delete Employee
@router.delete("/{employee_number}")
async def delete_employee(
    employee_number: int, session: Session = Depends(get_session)
):
    employee = session.get(Employee, employee_number)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    session.delete(employee)
    session.commit()
    return {"detail": "Employee deleted successfully"}
