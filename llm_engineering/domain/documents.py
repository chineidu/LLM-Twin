from abc import ABC

from pydantic import UUID4, Field

from .base import NoSQLBaseDocument
from .types import DataCategory


class UserDocument(NoSQLBaseDocument):
    first_name: str
    last_name: str

    class Settings:
        name: str = "users"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    

class Document(NoSQLBaseDocument, ABC):
    content: dict
    platform: str
    authod_id: UUID4 = Field(alias="author_id")
    author_full_name: str = Field(alias="author_full_name")


class RepositoryDocument(Document):
    name: str
    link: str

    class Settings:
        name = DataCategory.REPOSITORIES

class PostDocument(Document):
    image: str | None = None
    link: str | None = None

    class Settings:
        name = DataCategory.POSTS

class ArticleDocument(Document):
    link: str | None = None

    class Settings:
        name = DataCategory.ARTICLES