from typing import Annotated
from starlette import status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.database.database import get_db
from app.models import User
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from app.schemas import Create_User, User_log_In, User_delete
from app.auth import get_current_user, create_access_token, authenticate_user, bcrypt_context


import os
from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


router = APIRouter(
    prefix= "/user",
    tags=["User"]

)


@router.post("/sign_up")
def sign_up(user: Create_User , db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is not None:
        return JSONResponse(content={
                    "message": "User Already Existed", 
                    "status":406},
                    status_code=status.HTTP_406_NOT_ACCEPTABLE)
    create_user = User(
        username = user.username,
        email = user.email,
        hashed_password = bcrypt_context.hash(user.password),
    )
    db.add(create_user)
    db.commit()
    db.refresh(create_user)
    return JSONResponse(content={
                    "message": "User Account Created Successfully",
                    "data": {"id": create_user.id, "name": create_user.username, "email": create_user.email}, 
                    "status":200},
                    status_code=status.HTTP_200_OK)


@router.post("/log_in")
def log_In(user: User_log_In, db: Session = Depends(get_db)):

    user = authenticate_user(user.email, user.password, db)
    if not user: 
        return JSONResponse(content={
                    "message": "User Does not exist", 
                    "status": 404},
                    status_code=status.HTTP_404_NOT_FOUND)
    token = create_access_token(user.email , timedelta(int(ACCESS_TOKEN_EXPIRE_MINUTES)))

    return JSONResponse(content={
        'message':"login succefully","status_code":200,
        "access_token":token,
        "data":{"id" :user.id,  "email":user.email}},
                            status_code=status.HTTP_200_OK)

 
@router.delete("/delete_user")
def delet_user(user: User_delete, current_user: Annotated[dict, Depends(get_current_user)],db: Session = Depends(get_db)):
    delete_user = authenticate_user(current_user.email, user.password, db)
    if delete_user.id == current_user.id:    
        db_user = db.query(User).filter(User.id == delete_user.id).first()
        db_user.deleted_at = datetime.now()
        db.commit()
        db.refresh(db_user) 
        return JSONResponse(content={
        'message':"User Deleted Succefully","status_code":200,
        "data":{"id" :user.id,  "email":user.email}},
                            status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(content={"message": "You don't have permission to perform this action", "status": 401}, status_code=status.HTTP_401_UNAUTHORIZED)