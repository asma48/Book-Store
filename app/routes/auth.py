from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token, PasswordResetRequest, PasswordReset
from app.auth import get_password_hash, verify_password, create_access_token, create_verification_token, create_reset_token
from app.config import settings
from app.dependencies import get_current_user
from fastapi.responses import JSONResponse
from starlette import status

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):


    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user.email == user_data.email:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return JSONResponse(content={"message": "User Created Successfully", 
                                "data" : {
                                "email" : db_user.email,
                                "username" : db_user.username}
                                }, 
                                 status_code=status.HTTP_200_OK)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        return JSONResponse(content={"message": "Incorrect email or password"}, 
                                    status_code=status.HTTP_401_UNAUTHORIZED)
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return JSONResponse(content={"message": "User LogIn Successfully", 
                                "data" : {"access_token": access_token, "token_type": "bearer"}}, 
                                status_code=status.HTTP_200_OK)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    password_reset: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Send password reset email"""
    user = db.query(User).filter(User.email == password_reset.email).first()
    
    if not user:
        # Don't reveal if user exists or not
        return {"message": "If the email exists, a password reset link has been sent"}
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    db.commit()
    
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    password_reset: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    user = db.query(User).filter(User.reset_token == password_reset.token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update password
    user.hashed_password = get_password_hash(password_reset.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    
    db.commit()
    
    return {"message": "Password reset successfully"}



@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):


    current_user
    return JSONResponse(content={"message": "Current User Data", 
                                "data" : current_user}, 
                                status_code=status.HTTP_302_FOUND)
