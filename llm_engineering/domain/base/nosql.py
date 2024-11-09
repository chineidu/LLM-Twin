import uuid
from abc import ABC
from typing import Any, Generic, Type, TypeVar

from loguru import logger
from pydantic import BaseModel, Field, UUID4
from pymongo import errors

from llm_engineering.domain.exceptions import ImproperlyConfiguredException
from llm_engineering.infra.db.mongo import connection
from llm_engineering.settings import settings

_database = connection.get_database(settings.DATABASE_NAME)

T = TypeVar("T", bound="NoSQLBaseDocument")


class NoSQLBaseDocument(BaseModel, ABC, Generic[T]):
    """
    Base class for NoSQL database documents.

    Attributes
    ----------
    id : UUID4
        Unique identifier for the document, auto-generated using UUID4.
    """

    id: UUID4 = Field(default_factory=uuid.uuid4)

    def __eq__(self, value: object) -> bool:
        """
        Check equality between two NoSQL documents.

        Parameters
        ----------
        value : object
            Object to compare with.

        Returns
        -------
        bool
            True if documents are equal, False otherwise.
        """
        if not isinstance(value, self.__class__):
            return False

        return self.id == value.id

    def __hash__(self) -> int:
        """
        Generate hash value for the document.

        Returns
        -------
        int
            Hash value based on document ID.
        """
        return hash(self.id)

    @classmethod
    def from_mongo(cls: Type[T], data: dict) -> T:
        """
        Create document instance from MongoDB data.

        Parameters
        ----------
        data : dict
            MongoDB document data.

        Returns
        -------
        T
            Instance of document class.

        Raises
        ------
        ValueError
            If data is empty.
        """
        if not data:
            raise ValueError("Data cannot be empty.")

        id = data.get("_id")

        return cls(**dict(data, id=id))

    def model_dump(self: T, **kwargs) -> dict[str, Any]:
        """
        Convert document to dictionary format.

        Parameters
        ----------
        **kwargs : dict
            Additional arguments for model dumping.

        Returns
        -------
        dict
            Document data in dictionary format.
        """
        dict_: dict[str, Any] = super().model_dump(**kwargs)

        for key, value in dict_.items():
            if isinstance(value, uuid.UUID):
                dict_[key] = str(value)

        return dict_

    def to_mongo(self: T, **kwargs) -> dict:
        """
        Convert document to MongoDB format.

        Parameters
        ----------
        **kwargs : dict
            Additional arguments for conversion.

        Returns
        -------
        dict
            Document data in MongoDB format.
        """
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", False)

        parsed: dict[str, Any] = self.model_dump(
            exclude_unset=exclude_unset, by_alias=by_alias, **kwargs
        )
        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        for key, value in parsed.items():
            if isinstance(value, uuid.UUID):
                parsed[key] = str(value)

        return parsed

    def save(self: T, **kwags) -> T | None:
        """
        Save document to MongoDB.

        Parameters
        ----------
        **kwags : dict
            Additional arguments for saving.

        Returns
        -------
        T | None
            Saved document instance or None if save failed.
        """
        collection = _database[self.get_collection_name()]

        try:
            collection.insert_one(self.to_mongo(**kwags))
            return self
        except errors.WriteError:
            logger.exception(
                f"Failed to save document {self.id} "
                f"in collection {self.get_collection_name()}."
            )
            return None

    @classmethod
    def get_or_create(cls: Type[T], **filter_options) -> T:
        """
        Get existing document or create new one.

        Parameters
        ----------
        **filter_options : dict
            Filter criteria for document lookup.

        Returns
        -------
        T
            Retrieved or created document instance.

        Raises
        ------
        errors.OperationFailure
            If database operation fails.
        """
        collection = _database[cls.get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return cls.from_mongo(instance)

            new_instance = cls(**filter_options)
            new_instance = new_instance.save()

            return new_instance

        except errors.OperationFailure:
            logger.exception(
                f"Failed to retrieve document with filter options {filter_options}."
            )
            raise

    @classmethod
    def bulk_insert(cls: Type[T], documents: list[T], **kwargs) -> bool:
        """
        Insert multiple documents at once.

        Parameters
        ----------
        documents : list[T]
            List of documents to insert.
        **kwargs : dict
            Additional arguments for insertion.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        collection = _database[cls.get_collection_name()]

        try:
            collection.insert_many(doc.to_mongo(**kwargs) for doc in documents)

            return True
        except (errors.BulkWriteError, errors.WriteError):
            logger.error(f"Failed to bulk insert documents of type {cls.__name__}.")
            return False

    @classmethod
    def find(cls: Type[T], **filter_options) -> T | None:
        """
        Find a single document matching filter criteria.

        Parameters
        ----------
        **filter_options : dict
            Filter criteria for document lookup.

        Returns
        -------
        T | None
            Matching document instance or None if not found.
        """
        collection = _database[cls.get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return cls.from_mongo(instance)

            return None

        except errors.OperationFailure:
            logger.exception(
                f"Failed to retrieve document with filter options {filter_options}."
            )
            return None

    @classmethod
    def bulk_find(cls: Type[T], **filter_options) -> list[T]:
        """
        Find multiple documents matching filter criteria.

        Parameters
        ----------
        **filter_options : dict
            Filter criteria for documents lookup.

        Returns
        -------
        list[T]
            List of matching document instances.
        """
        collection = _database[cls.get_collection_name()]
        try:
            instances = collection.find(filter_options)
            return [
                document
                for instance in instances
                if (document := cls.from_mongo(instance)) is not None
            ]

        except errors.OperationFailure:
            logger.exception(
                f"Failed to retrieve document with filter options {filter_options}."
            )
            return []

    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        """
        Get MongoDB collection name from Settings.

        Returns
        -------
        str
            Collection name.

        Raises
        ------
        ImproperlyConfiguredException
            If Settings class or name attribute is missing.
        """
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ImproperlyConfiguredException(
                "Document should define a 'Settings' configuration class "
                "with the name of the collection."
            )
        return cls.Settings.name
