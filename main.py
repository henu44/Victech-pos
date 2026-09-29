from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
# from passlib.context import CryptContext
import bcrypt


from database import engine, Base, SessionLocal
import models


app = FastAPI()


# Create database tables
Base.metadata.create_all(bind=engine)


# Allow frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Password hashing
# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto"
# )


# Get database session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Data coming from HTML
class UserRegistration(BaseModel):
    fullname: str
    username: str
    email: str
    role:str
    password: str
    confirm_password: str


# data comming from cover.html
class LoginRequest(BaseModel):
    username: str
    password: str

# Data coming from product.html

class ProductStore(BaseModel):
    name: str
    category: str
    marked_price : float
    quantity : int

# sales data 
class SaleProduct(BaseModel):
    id : int
    quantity : int

class Sale(BaseModel):
    payment_type: str
    products :list[SaleProduct]




@app.get("/")
def home():
    return {
        "message": "Victech POS API is working"
    }


@app.post("/register")
def register(
    user: UserRegistration,
    db: Session = Depends(get_db)
):

    # Check passwords
    if user.password != user.confirm_password:
        return {
            "message": "Passwords do not match"
        }


    # Hash password
    # hashed_password = pwd_context.hash(user.password)

    hashed_password = bcrypt.hashpw(
    user.password.encode("utf-8"),
    bcrypt.gensalt()
    ).decode("utf-8")



    # Create user
    new_user = models.User(
        fullname=user.fullname,
        username=user.username,
        role = user.role,
        email=user.email,
        password_hash=hashed_password
    )


    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return {
        "message": "Account created successfully!",
        "username": new_user.username
    }


@app.post("/login")
async def login (data: LoginRequest):
    print("Username" ,  data.username)
    print('password received')

    return{
        "mm": "kkkk"
    }


@app.post("/products")
def products(product: ProductStore, db: Session = Depends(get_db)):

    # Check if the product already exists
    existing_product = db.query(models.Products).filter(
        models.Products.name == product.name,
        models.Products.category == product.category
    ).first()

    # If it already exists, increase its quantity
    if existing_product:
        existing_product.quantity += product.quantity

        db.commit()
        db.refresh(existing_product)

        return {
            "message": "Product stock updated successfully!",
            "product": existing_product.name,
            "quantity": existing_product.quantity
        }

    # If it does not exist, create a new product
    new_product = models.Products(
        name=product.name,
        category=product.category,
        marked_price=product.marked_price,
        quantity=product.quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product added successfully!",
        "product": new_product.name,
        "quantity": new_product.quantity
    }

@app.get("/products")
def get_products(db:Session = Depends(get_db)):
    products = db.query(models.Products).all()

    return products

@app.post("/sales")
def create_sales(sale: Sale, db: Session = Depends(get_db)):

    total_amount = 0

    # 1. Check all products and calculate total
    for item in sale.products:

        product = db.query(models.Products).filter(
            models.Products.id == item.id
        ).first()

        if not product:
            return {
                "message": "Product not found"
            }

        if product.quantity < item.quantity:
            return {
                "message": "Not enough stock"
            }

        total_amount += product.marked_price * item.quantity

    # 2. Create the main sale
    new_sale = models.Sale(
        payment_type=sale.payment_type,
        total_amount=total_amount
    )

    db.add(new_sale)
    db.flush()

    # 3. Create SaleItems and reduce stock
    for item in sale.products:

        product = db.query(models.Products).filter(
            models.Products.id == item.id
        ).first()

        sale_item = models.SaleItem(
            sale_id=new_sale.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.marked_price
        )

        db.add(sale_item)

        product.quantity -= item.quantity

    # 4. Save everything
    db.commit()

    return {
        "message": "Sale created successfully",
        "sale_id": new_sale.id,
        "total": new_sale.total_amount
    }
  

 