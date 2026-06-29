from typing import Generic, TypeVar
from app.core.base.repository import BaseRepository

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[RepositoryType]):
    """Abstract base service providing access to a repository."""

    def __init__(self, repository: RepositoryType):
        self.repository = repository
