from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from typing import Optional, List
from datetime import date

# from sqlalchemy.orm import relationship


class Office(SQLModel, table=True):
    __tablename__ = "offices"
    office_code: str = Field(primary_key=True, max_length=10)
    city: str = Field(max_length=50)
    phone: str = Field(max_length=50)
    address_line1: str = Field(max_length=50)
    address_line2: Optional[str] = Field(default=None, max_length=50)
    state: Optional[str] = Field(default=None, max_length=50)
    country: str = Field(max_length=50)
    postal_code: str = Field(max_length=15)
    territory: str = Field(max_length=10)

    employees: List["Employee"] = Relationship(back_populates="office")


class Employee(SQLModel, table=True):
    __tablename__ = "employees"

    employee_number: int = Field(primary_key=True)
    last_name: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    extension: str = Field(max_length=10)
    email: str = Field(max_length=100)
    office_code: str = Field(foreign_key="offices.office_code", max_length=10)
    reports_to: Optional[int] = Field(
        foreign_key="employees.employee_number", default=None
    )
    job_title: str = Field(max_length=50)

    office: Optional["Office"] = Relationship(back_populates="employees")
    manager: Optional["Employee"] = Relationship(
        back_populates="subordinates",
        sa_relationship_kwargs={"remote_side": "Employee.employee_number"},
    )
    subordinates: List["Employee"] = Relationship(back_populates="manager")
    customers: List["Customer"] = Relationship(back_populates="sales_rep_employee")


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    customer_number: int = Field(primary_key=True)
    customer_name: str = Field(max_length=50)
    contact_last_name: str = Field(max_length=50)
    contact_first_name: str = Field(max_length=50)
    phone: str = Field(max_length=50)
    address_line1: str = Field(max_length=50)
    address_line2: Optional[str] = Field(default=None, max_length=50)
    city: str = Field(max_length=50)
    state: Optional[str] = Field(default=None, max_length=50)
    postal_code: Optional[str] = Field(default=None, max_length=15)
    country: str = Field(max_length=50)
    sales_rep_employee_number: Optional[int] = Field(
        foreign_key="employees.employee_number", default=None
    )
    credit_limit: Optional[float] = Field(default=None)

    sales_rep_employee: Optional["Employee"] = Relationship(back_populates="customers")
    orders: List["Order"] = Relationship(back_populates="customer")
    payments: List["Payment"] = Relationship(back_populates="customer")


class ProductLine(SQLModel, table=True):
    __tablename__ = "productlines"

    product_line: str = Field(primary_key=True, max_length=50)
    text_description: Optional[str] = Field(default=None, max_length=4000)
    html_description: Optional[str] = Field(default=None)
    image: Optional[bytes] = Field(default=None)

    products: List["Product"] = Relationship(back_populates="product_lines")


class Product(SQLModel, table=True):
    __tablename__ = "products"

    product_code: str = Field(primary_key=True, max_length=15)
    product_name: str = Field(max_length=70)
    product_line: str = Field(foreign_key="productlines.product_line", max_length=50)
    product_scale: str = Field(max_length=10)
    product_vendor: str = Field(max_length=50)
    product_description: str = Field()
    quantity_in_stock: int = Field()
    buy_price: float = Field()
    msrp: float = Field()

    product_lines: Optional["ProductLine"] = Relationship(back_populates="products")
    order_details: List["OrderDetail"] = Relationship(back_populates="product")


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    order_number: int = Field(primary_key=True)
    order_date: date = Field()
    required_date: date = Field()
    shipped_date: Optional[date] = Field(default=None)
    status: str = Field(max_length=15)
    comments: Optional[str] = Field(default=None)
    customer_number: int = Field(foreign_key="customers.customer_number")

    customer: Optional["Customer"] = Relationship(back_populates="orders")
    order_details: List["OrderDetail"] = Relationship(back_populates="order")


class OrderDetail(SQLModel, table=True):
    __tablename__ = "orderdetails"

    order_number: int = Field(foreign_key="orders.order_number", primary_key=True)
    product_code: str = Field(foreign_key="products.product_code", primary_key=True)
    quantity_ordered: int = Field()
    price_each: float = Field()
    order_line_number: int = Field()

    order: Optional["Order"] = Relationship(back_populates="order_details")
    product: Optional["Product"] = Relationship(back_populates="order_details")


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    customer_number: int = Field(
        foreign_key="customers.customer_number", primary_key=True
    )
    check_number: str = Field(primary_key=True, max_length=50)
    payment_date: date = Field()
    amount: float = Field()

    customer: Optional["Customer"] = Relationship(back_populates="payments")


# Update forward references
Office.model_rebuild()
Employee.model_rebuild()
Customer.model_rebuild()
ProductLine.model_rebuild()
Product.model_rebuild()
Order.model_rebuild()
OrderDetail.model_rebuild()
Payment.model_rebuild()
