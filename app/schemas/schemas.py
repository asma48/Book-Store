from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class Create_User(BaseModel):
    username: str
    email: EmailStr
    password: str
        
class User_log_In(BaseModel):
    email: EmailStr
    password : str

class User_delete(BaseModel):
    email: EmailStr
    password : str


class Current_User(BaseModel):
    email : EmailStr  


# Book Schemas
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    isbn: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    isbn: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)


class BookUpdate(BookBase):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, ge=0)


class BookResponse(BookBase):
    id: int
    user_id: int
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Search and Pagination Schemas
class BookSearch(BaseModel):
    query: Optional[str] = None
    author: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    size: int
    pages: int
