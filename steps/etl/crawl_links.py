from typing import Annotated
from urllib import urlparse

from loguru import logger
from tdqm import tqdm
from zenml import get_step_context, step

from llm_engineering.application.crawlers.dispatcher import CrawlerDispatcher
from llm_engineering.domain.documents import UserDocument