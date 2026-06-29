from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.core.database import get_db
from app import models, schemas
from app.services.user import UserService
from app.use_cases.users.queries import GetUserByIdQuery, ListUsersQuery
from app.use_cases.users.commands import UpdateUserCommand, DeleteUserCommand

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(current_user: models.User = Depends(deps.get_current_user)):
    """Retrieve profile of the authenticated user."""
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Update profile of the authenticated user."""
    svc = UserService(db)
    return UpdateUserCommand(
        user=current_user,
        service=svc,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        is_active=user_in.is_active,
    ).execute()

@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """List all registered users (requires authentication)."""
    return ListUsersQuery(service=UserService(db), skip=skip, limit=limit).execute()

@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Get a specific user by ID."""
    user = GetUserByIdQuery(user_id=user_id, service=UserService(db)).execute()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Delete a user account by ID."""
    svc = UserService(db)
    user = GetUserByIdQuery(user_id=user_id, service=svc).execute()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return DeleteUserCommand(user=user, service=svc).execute()
