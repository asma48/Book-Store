from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.database.database import get_db
from app.models.models import Book, User
from app.schemas.schemas import BookCreate, BookUpdate, BookResponse, BookSearch, PaginationParams, PaginatedResponse
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    if book_data.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book_data.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists"
            )
    db_book = Book(
        title = book_data.title,
        author = book_data.author,
        description = book_data.description,
        isbn = book_data.isbn,
        price = book_data.price,
        user_id = current_user.id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return db_book


@router.get("/", response_model=PaginatedResponse)
async def get_books(
    title: Optional[str] = Query(None, description="Search by book title"),
    author: Optional[str] = Query(None, description="Search by author name"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    size: int = Query(10, ge=1, le=100, description="Books per page"),
    db: Session = Depends(get_db)
):

    query = db.query(Book)

    if title:
        query = query.filter(Book.title == title)
        total = query.count()
  
    if author:
        query = query.filter(Book.author == author)
        total = query.count()

    if title is None and author is None:
        total = query.count()
 

    offset = (page - 1) * size
    books = query.offset(offset).limit(size).all()
    pages = (total + size - 1) // size if total else 1


    
    return PaginatedResponse(
        items=books,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    return book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):

    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if ISBN already exists (if changing)
    if book_data.isbn and book_data.isbn != book.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book_data.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists"
            )
    
    # Update book data
    for field, value in book_data.dict(exclude_unset=True).items():
        setattr(book, field, value)
    
    db.commit()
    db.refresh(book)
    
    
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
  
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(book)
    db.commit()
    return {"message" : "Book Deleted Successfully"}


@router.get("/my/books", response_model=List[BookResponse])
async def get_my_books(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    
    books = db.query(Book).filter(Book.user_id == current_user.id).all()
    return books
