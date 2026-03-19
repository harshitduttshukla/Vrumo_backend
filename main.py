from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from database import engine
from database_models import Base

from routers import users, services, bookings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vrumo API",
    description="Backend for Vrumo Car and Bike Services",
    version="0.0.1"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("❌ VALIDATION ERROR:", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.get("/")
def root():
    return {"message": "🚀 Vrumo API is running"}

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(services.router, prefix="/services", tags=["Services"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

