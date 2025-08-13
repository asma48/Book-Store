# Bookstore API

A FastAPI microservice for a mini "Bookstore" with authentication, search, and file upload capabilities.

## Features

- **User Authentication**: Register, login, email verification, and password reset
- **Book Management**: CRUD operations for books with search and pagination
- **File Upload**: Support for book files (PDF, EPUB, etc.) and cover images
- **Search & Pagination**: Advanced search with filters and pagination
- **Security**: JWT tokens, password hashing, and role-based access control
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Documentation**: Auto-generated API docs with Swagger UI and ReDoc

## Directory Structure

```
Bookstore/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── dependencies.py      # FastAPI dependencies
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── books.py         # Book management endpoints
│   │   └── upload.py        # File upload endpoints
│   └── services/
│       ├── __init__.py
│       └── email_service.py # Email service
├── alembic/                 # Database migrations
├── uploads/                 # File upload directory
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── alembic.ini            # Alembic configuration
└── README.md              # This file
```

## Prerequisites

- Python 3.8+
- PostgreSQL database
- SMTP server (for email functionality)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Bookstore
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb bookstore_db
   
   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

## Running the Application

1. **Start the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - API Base URL: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc


## Database Migrations

If you need to make database schema changes:

1. **Create a new migration**
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations**
   ```bash
   alembic upgrade head
   ```

3. **Rollback migrations**
   ```bash
   alembic downgrade -1
   ```


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.