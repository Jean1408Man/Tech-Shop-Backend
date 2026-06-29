from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import get_db
from app import schemas
from app.services.user import UserService
from app.use_cases.users.commands import RegisterUserCommand, AuthenticateUserCommand

router = APIRouter()

@router.post("/register", response_model=schemas.User, status_code=201)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    svc = UserService(db)
    try:
        return RegisterUserCommand(
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name,
            service=svc,
        ).execute()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 token login — returns JWT access token."""
    svc = UserService(db)
    user = AuthenticateUserCommand(
        email=form_data.username,
        password=form_data.password,
        service=svc,
    ).execute()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user."
        )

    return {
        "access_token": security.create_access_token(subject=user.email),
        "token_type": "bearer",
    }
