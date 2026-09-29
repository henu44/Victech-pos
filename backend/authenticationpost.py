from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Authentication"])

@router.post("/login")
def login():
    return {"message": "Login successful"}

@router.post("/signup")
def signup():
    return {"message": "Signup successful"}