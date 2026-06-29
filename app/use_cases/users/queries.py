from typing import Optional, List
from dataclasses import dataclass

from app.core.base.use_case import BaseQuery
from app.models.user import User
from app.services.user import UserService


@dataclass
class GetUserByIdQuery(BaseQuery[Optional[User]]):
    user_id: int
    service: UserService

    def execute(self) -> Optional[User]:
        return self.service.get_by_id(self.user_id)


@dataclass
class GetUserByEmailQuery(BaseQuery[Optional[User]]):
    email: str
    service: UserService

    def execute(self) -> Optional[User]:
        return self.service.get_by_email(self.email)


@dataclass
class ListUsersQuery(BaseQuery[List[User]]):
    service: UserService
    skip: int = 0
    limit: int = 100

    def execute(self) -> List[User]:
        return self.service.get_all(skip=self.skip, limit=self.limit)
