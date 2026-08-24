from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.tourism import (
    attraction_router,
    destination_router,
    hotel_router,
    local_event_router,
    restaurant_router,
)
from app.core.database import get_db
from app.core.exception_handlers import register_exception_handlers
from app.routers import auth, users

app = FastAPI(title="AI Tourism Planning System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(destination_router)
app.include_router(attraction_router)
app.include_router(hotel_router)
app.include_router(restaurant_router)
app.include_router(local_event_router)

register_exception_handlers(app)

# All API routes are versioned under /api/v1, per docs/api-contract.md.
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Basic liveness check for the API process."""
    return {"status": "ok"}


@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    """Basic check that the API can reach the database."""
    db.execute(text("SELECT 1"))
    return {"status": "database connection successful"}
