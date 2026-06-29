from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app import schemas
from app.services.item import ItemService
from app.use_cases.items.commands import CreateItemCommand
from app.use_cases.items.queries import ListItemsQuery

router = APIRouter()

@router.post("/", response_model=schemas.Item, status_code=201)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new item."""
    return CreateItemCommand(
        title=item.title,
        description=item.description,
        service=ItemService(db),
    ).execute()

@router.get("/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of items."""
    return ListItemsQuery(service=ItemService(db), skip=skip, limit=limit).execute()
