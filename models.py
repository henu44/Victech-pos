from sqlalchemy import Column, Integer, String ,Float,ForeignKey
from database import Base
from sqlalchemy import DateTime
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    fullname = Column(String(100), nullable=False)

    username = Column(
        String(50),
        unique=True,
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False
    )
    email = Column(
        String(150),
        unique = False,
        nullable = False
    )
    role = Column(
        String(50),
        default= "cashier",
        nullable = False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

class Products(Base):
    __tablename__ = "Products"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(100) ,nullable = False)
    category = Column(String(100), nullable = False)
    marked_price = Column(Float)
    quantity = Column(Integer, default = 0)


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer,primary_key= True, index = True)
    payment_type =Column(String(50), nullable = False)
    total_amount = Column(Float , nullable= False)
    sale_date = Column(DateTime, default = datetime.now, nullable = False)

class SaleItem(Base):
    __tablename__ = "sale_items"
    
    id = Column(Integer,primary_key = True,index = True)
    sale_id = Column(Integer , ForeignKey("sales.id"),nullable = False)
    product_id = Column(Integer , ForeignKey(Products.id) , nullable = False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)