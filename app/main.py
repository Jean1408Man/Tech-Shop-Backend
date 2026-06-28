from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.config import settings
from app.database import engine, Base, get_db
from app import models, schemas

# NOTE: Database schemas are managed via Alembic migrations.

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Orbita API!"}

@app.get("/health", status_code=200)
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to verify DB connection
        db.execute(models.Base.metadata.tables["items"].select().limit(1))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {e}"
        
    return {
        "status": "healthy",
        "database": db_status,
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.post("/items/", response_model=schemas.Item, status_code=201)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(title=item.title, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items
