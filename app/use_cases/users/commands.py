from typing import Optional
from dataclasses import dataclass

from app.core.base.use_case import BaseCommand
from app.models.user import User
from app.services.user import UserService


@dataclass
class RegisterUserCommand(BaseCommand[User]):
    email: str
    password: str
    service: UserService
    full_name: Optional[str] = None

    def execute(self) -> User:
        return self.service.create(
            email=self.email,
            password=self.password,
            full_name=self.full_name,
        )


@dataclass
class AuthenticateUserCommand(BaseCommand[Optional[User]]):
    email: str
    password: str
    service: UserService

    def execute(self) -> Optional[User]:
        return self.service.authenticate(self.email, self.password)


@dataclass
class UpdateUserCommand(BaseCommand[User]):
    user: User
    service: UserService
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

    def execute(self) -> User:
        return self.service.update(
            self.user,
            email=self.email,
            password=self.password,
            full_name=self.full_name,
            is_active=self.is_active,
        )


@dataclass
class DeleteUserCommand(BaseCommand[User]):
    user: User
    service: UserService

    def execute(self) -> User:
        return self.service.delete(self.user)
