# Vrumo Backend API

Backend service for Vrumo Car and Bike Services, built with FastAPI, PostgreSQL, and SQLAlchemy.

## 🚀 Features

- **User Management**: Registration and user retrieval.
- **Service Management**: CRUD operations for various car and bike services.
- **Role-based access**: Support for customer and admin roles.
- **Database Integration**: PostgreSQL with SQLAlchemy ORM.

## 🛠 Prerequisites

- Python 3.9+
- PostgreSQL
- Virtual environment (recommended)

## 📥 Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd project/Backend
```

### 2. Create and activate a virtual environment
```bash
python -m venv myenv
# Windows:
myenv\Scripts\activate
# Linux/macOS:
source myenv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `Backend` directory and add your PostgreSQL credentials:
```env
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vrumo_db
```

### 5. Database Initialization
The application automatically creates tables on startup. Ensure your PostgreSQL server is running and the database specified in `.env` exists.

## 🏃 Running the Application
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## 📖 API Documentation
Once the server is running, you can access the interactive API docs:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 📂 Project Structure
- `main.py`: Application entry point and router inclusion.
- `database.py`: Database connection and session management.
- `database_models.py`: SQLAlchemy database models.
- `schemas.py`: Pydantic models for request/response validation.
- `routers/`: API route handlers (users, services).
- `utils.py`: Utility functions (e.g., password hashing).