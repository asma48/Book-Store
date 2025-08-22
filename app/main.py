from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import auth, books, upload
from app.database.database import engine
from app.models.models import Base


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bookstore API",
    description="A FastAPI microservice for a mini Bookstore with authentication, search, and file upload",
)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(upload.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Bookstore API",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "bookstore-api"}



@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
