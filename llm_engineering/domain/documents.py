from abc import ABC

from pydantic import UUID4, Field

from .base import NoSQLBaseDocument
from .types import DataCategory


class UserDocument(NoSQLBaseDocument):
    """
    Document representing a user in the system.

    Attributes
    ----------
    first_name : str
        The user's first name
    last_name : str
        The user's last name
    """
    first_name: str
    last_name: str

    class Settings:
        name: str = "users"

    @property
    def full_name(self) -> str:
        """
        Get the user's full name.

        Returns
        -------
        str
            The concatenated first and last name
        """
        return f"{self.first_name} {self.last_name}"
    

class Document(NoSQLBaseDocument, ABC):
    """
    Abstract base class for all document types.

    Attributes
    ----------
    content : dict
        The document's content
    platform : str
        The platform where the document originates
    authod_id : UUID4
        The unique identifier of the document's author
    author_full_name : str
        The full name of the document's author
    """
    content: dict
    platform: str
    authod_id: UUID4 = Field(alias="author_id")
    author_full_name: str = Field(alias="author_full_name")


class RepositoryDocument(Document):
    """
    Document representing a code repository.

    Attributes
    ----------
    name : str
        The name of the repository
    link : str
        The URL link to the repository
    """
    name: str
    link: str

    class Settings:
        name = DataCategory.REPOSITORIES

class PostDocument(Document):
    """
    Document representing a social media post.

    Attributes
    ----------
    image : str | None
        The URL of the post's image, if any
    link : str | None
        The URL link to the post, if any
    """
    image: str | None = None
    link: str | None = None

    class Settings:
        name = DataCategory.POSTS

class ArticleDocument(Document):
    """
    Document representing an article.

    Attributes
    ----------
    link : str | None
        The URL link to the article, if any
    """
    link: str | None = None

    class Settings:
        name = DataCategory.ARTICLES