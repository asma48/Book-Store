from starlette import status
from jose import jwt, JWTError
from datetime import timedelta, datetime
from app.models import User
from passlib.context import CryptContext
from app.database.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import Current_User
import os
from dotenv import load_dotenv
load_dotenv()



SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')


bcrypt_context =  CryptContext(schemes= ['bcrypt'], deprecated= 'auto')

bearer_scheme = HTTPBearer()


def authenticate_user(email: str, password:str , db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User does not exist")
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Incorrect Password")
    return user



def create_access_token(email: str, expire_delta: timedelta):
    encode = {'sub': email }
    expires = expire_delta + datetime.now()
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm= ALGORITHM)

 
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):  
    
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized user"
            )
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

            return user
        except JWTError:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorize user"
        )