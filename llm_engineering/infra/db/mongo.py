from typing import Any
from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from llm_engineering.settings import settings


class MongoDatabaseConnector:
    """
    A singleton class that manages MongoDB database connections.

    This class implements the singleton pattern to ensure only one MongoDB
    connection is created and reused throughout the application lifecycle.

    Attributes
    ----------
    _instance : MongoClient | None
        The singleton instance of the MongoDB client connection.

    Returns
    -------
    MongoClient
        A connected MongoDB client instance.
    """

    _instance: MongoClient | None = None

    def __new__(cls, *args: tuple[Any], **kwargs: dict[str, Any]) -> MongoClient:
        """
        Create or return the existing MongoDB client connection.

        Parameters
        ----------
        *args : tuple
            Variable positional arguments.
        **kwargs : dict
            Variable keyword arguments.

        Returns
        -------
        MongoClient
            The MongoDB client connection instance.

        Raises
        ------
        ConnectionFailure
            If the connection to MongoDB fails.
        """
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.DATABASE_HOST)
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e!s}")
                raise

        logger.info(f"Connected to MongoDB URI successfully: {settings.DATABASE_HOST}")
        return cls._instance


connection: MongoClient = MongoDatabaseConnector()
