from urllib.parse import urlparse
from typing import Optional, Dict, Any

from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers.html2text import Html2TextTransformer
from loguru import logger

from llm_engineering.domain.documents import ArticleDocument
from .base import BaseCrawler


class CustomArticleCrawler(BaseCrawler):
    """
    A crawler for extracting and storing custom articles.

    Attributes
    ----------
    model : ArticleDocument
        The document model for storing article data.
    """

    model: ArticleDocument

    def __init__(self) -> None:
        """
        Initialize the CustomArticleCrawler.
        """
        super().__init__()

    def extract(self, link: str, **kwargs: Any) -> None:
        """
        Extract article content from a given URL and store it in the database.

        Parameters
        ----------
        link : str
            The URL of the article to extract.
        **kwargs : Any
            Additional keyword arguments.
            Expected to contain 'user' with attributes 'id' and 'full_name'.

        Returns
        -------
        None
        """
        old_model: Optional[ArticleDocument] = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Article already exists in the database: {link}")
            return

        logger.info(f"Extracting article: {link}")
        loader: AsyncHtmlLoader = AsyncHtmlLoader([link])
        docs = loader.load()

        html2text: Html2TextTransformer = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        doc_transformed = docs_transformed[0]

        content: Dict[str, Optional[str]] = {
            "Title": doc_transformed.metadata.get("title"),
            "Subtile": doc_transformed.metadata.get("description"),
            "Author": doc_transformed.page_content,
            "Language": doc_transformed.metadata.get("language"),
        }

        parsed_url = urlparse(link)
        platform: str = parsed_url.netloc

        user = kwargs.get("user")
        instance: ArticleDocument = self.model(
            author_id=user.id,  # type: ignore
            author_full_name=user.full_name,  # type: ignore
            content=content,
            platform=platform,
            link=link,
        )

        instance.save()

        logger.info(f"Custom article extracted and saved: {link}")
