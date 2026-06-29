from typing import Optional
from sqlalchemy.orm import Session

from app.core.base.service import BaseService
from app.core import security
from app.repositories.user import UserRepository
from app.models.user import User

class UserService(BaseService[UserRepository]):
    """Domain service for user business logic."""

    def __init__(self, db: Session):
        super().__init__(UserRepository(db))

    def get_by_email(self, email: str) -> Optional[User]:
        return self.repository.get_by_email(email)

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.repository.get(user_id)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip=skip, limit=limit)

    def create(self, email: str, password: str, full_name: Optional[str] = None) -> User:
        existing = self.repository.get_by_email(email)
        if existing:
            raise ValueError(f"User with email '{email}' already exists.")
        user = User(
            email=email,
            hashed_password=security.get_password_hash(password),
            full_name=full_name,
        )
        return self.repository.create(user)

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.repository.get_by_email(email)
        if not user or not security.verify_password(password, user.hashed_password):
            return None
        return user

    def update(self, user: User, **fields) -> User:
        if "password" in fields and fields["password"]:
            user.hashed_password = security.get_password_hash(fields.pop("password"))
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        return self.repository.update(user)

    def delete(self, user: User) -> User:
        return self.repository.delete(user)
