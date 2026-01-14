import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas, auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Validate password strength
    is_valid, error_msg = auth.validate_password(user.password)
    if not is_valid:
        logger.warning(f"Password validation failed for email: {user.email}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Basic email validation
    if "@" not in user.email or "." not in user.email.split("@")[1]:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    existing = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing:
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        new_user = models.User(
            email=user.email,
            hashed_password=auth.hash_password(user.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {user.email}")
        return {"message": "User registered successfully"}
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user:
        logger.warning(f"Login attempt with invalid email: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not auth.verify_password(user.password, db_user.hashed_password):
        logger.warning(f"Login attempt with invalid password for: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": db_user.email})
    logger.info(f"User logged in: {user.email}")

    return {
        "access_token": token,
        "token_type": "bearer"
    }
