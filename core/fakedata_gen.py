# from .in_models import User, Product, Order, Payment, SQLModel
# from sqlmodel import Session, create_engine
# from faker import Faker
# from passlib.context import CryptContext
# import random
# from .in_config import DATABASE_URL


# def generate_data():
#     fake = Faker()
#     engine = create_engine(DATABASE_URL, echo=True)
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#     # Create tables
#     SQLModel.metadata.create_all(engine)

#     # Generate data
#     with Session(engine) as session:
#         # Create Users
#         users = [
#             User(
#                 user_name=fake.user_name(),
#                 email=fake.email(),
#                 full_name=fake.name(),
#                 hashed_password=pwd_context.hash("Python123"),
#             )
#             for _ in range(50)
#         ]
#         session.add_all(users)
#         session.commit()

#         # Create Products
#         products = [
#             Product(
#                 product_code=fake.unique.bothify(text="???-#####"),
#                 product_name=fake.word(),
#                 product_description=fake.text(max_nb_chars=50),
#                 quantity_in_stock=random.randint(10, 100),
#                 price=round(random.uniform(10.0, 500.0), 2),
#             )
#             for _ in range(100)
#         ]
#         session.add_all(products)
#         session.commit()

#         # Create Orders
#         orders = [
#             Order(
#                 order_date=fake.date_time_this_year(),
#                 required_date=fake.date_time_this_year(),
#                 shipped_date=(
#                     fake.date_time_this_year() if random.choice([True, False]) else None
#                 ),
#                 status=random.choice(["Shipped", "Cancelled", "Pending"]),
#                 comments=fake.sentence(nb_words=20),
#                 user_id=random.choice(users).user_id,
#                 product_code=random.choice(products).product_code,
#             )
#             for _ in range(30)
#         ]
#         session.add_all(orders)
#         session.commit()

#         # Create Payments
#         payments = [
#             Payment(
#                 order_number=random.choice(orders).order_number,
#                 payment_date=fake.date_time_this_year(),
#                 amount=round(random.uniform(20.0, 1000.0), 2),
#                 payment_method=random.choice(
#                     ["Credit Card", "PayPal", "Bank Transfer"]
#                 ),
#             )
#             for _ in range(20)
#         ]
#         session.add_all(payments)
#         session.commit()


# if __name__ == "__main__":
#     generate_data()
