import os
import aiofiles
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Book, User
from app.schemas import BookResponse
from app.dependencies import get_current_active_user
from app.config import settings

router = APIRouter(prefix="/upload", tags=["file upload"])


async def save_upload_file(upload_file: UploadFile, folder: str) -> str:
    """Save uploaded file and return file path"""
    # Create upload directory if it doesn't exist
    os.makedirs(folder, exist_ok=True)
    
    # Generate unique filename
    import uuid
    file_extension = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(folder, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    
    return file_path


@router.post("/book-file/{book_id}")
async def upload_book_file(
    book_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload book file (PDF, EPUB, etc.)"""
    # Check if book exists and user owns it
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate file type
    allowed_extensions = ['.pdf', '.epub', '.mobi', '.txt', '.doc', '.docx']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024):.1f}MB"
        )
    
    # Save file
    upload_folder = os.path.join(settings.upload_dir, "books")
    file_path = await save_upload_file(file, upload_folder)
    
    # Update book record
    book.file_path = file_path
    db.commit()
    
    return {"message": "Book file uploaded successfully", "file_path": file_path}


@router.post("/cover-image/{book_id}")
async def upload_cover_image(
    book_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload book cover image"""
    # Check if book exists and user owns it
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size / (1024*1024):.1f}MB"
        )
    
    # Save file
    upload_folder = os.path.join(settings.upload_dir, "covers")
    file_path = await save_upload_file(file, upload_folder)
    
    # Update book record
    book.cover_image = file_path
    db.commit()
    
    return {"message": "Cover image uploaded successfully", "file_path": file_path}


@router.get("/files/{file_path:path}")
async def download_file(file_path: str):
    """Download uploaded file"""
    full_path = os.path.join(settings.upload_dir, file_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(full_path)


@router.delete("/book-file/{book_id}")
async def delete_book_file(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete book file"""
    # Check if book exists and user owns it
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not book.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file to delete"
        )
    
    # Delete file from filesystem
    if os.path.exists(book.file_path):
        os.remove(book.file_path)
    
    # Update book record
    book.file_path = None
    db.commit()
    
    return {"message": "Book file deleted successfully"}


@router.delete("/cover-image/{book_id}")
async def delete_cover_image(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete cover image"""
    # Check if book exists and user owns it
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not book.cover_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No cover image to delete"
        )
    
    # Delete file from filesystem
    if os.path.exists(book.cover_image):
        os.remove(book.cover_image)
    
    # Update book record
    book.cover_image = None
    db.commit()
    
    return {"message": "Cover image deleted successfully"}
