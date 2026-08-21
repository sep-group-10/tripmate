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

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "database connection successful"}
