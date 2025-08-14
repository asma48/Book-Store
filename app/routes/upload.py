import csv
import io
import os
import aiofiles
from typing import Annotated, List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Book, User
from app.schemas.schemas import BookResponse
from app.middleware.auth import get_current_user


router = APIRouter(prefix="/upload", tags=["file upload"])


def insert_books_from_csv(file: UploadFile, db: Session):
    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(contents))

    books_to_insert = []
    for row in reader:
        books_to_insert.append(
            Book(
                title=row["title"],
                author=row["author"],
                description=row.get("description"),
                isbn=row["isbn"],
                price=float(row["price"])
            )
        )

    db.bulk_save_objects(books_to_insert)
    db.commit()
    return len(books_to_insert)


@router.post("/books/upload")
def upload_books_sync(current_user: Annotated[User, Depends(get_current_user)], file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    count = insert_books_from_csv(file, db)
    return {"inserted_records": count}


