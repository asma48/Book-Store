import csv
import io
from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Book, User
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/upload", tags=["file upload"])

@router.post("/books/upload")
def upload_books_sync(
    current_user: Annotated[User, Depends(get_current_user)], 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:

        contents = file.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(contents))

        total_records = 0
        for row in reader:
            book = Book(
                user_id = current_user.id,
                title=row["title"],
                author=row["author"],
                description=row.get("description"),
                isbn=row["isbn"],
                price=float(row["price"])
            )
            db.add(book)
            db.commit()
            total_records += 1
         

        db.refresh(book)


        return {"inserted_records": total_records}
    except Exception as e:
        return {"error": str(e)}
