import uuid
from abc import ABC
from typing import Generic, Type, TypeVar

from loguru import logger
from pydantic import BaseModel, Field, UUID4
from pymongo import errors
