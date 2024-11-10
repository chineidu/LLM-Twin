from typing import Any
from bs4 import BeautifulSoup
from loguru import logger

from llm_engineering.domain.documents import ArticleDocument

from .base import BaseSeleniumCrawler


class MediumCrawler(BaseSeleniumCrawler):
    """
    A crawler class for extracting articles from Medium platform.

    Attributes
    ----------
    model : ArticleDocument
        The document model class for storing article data.
    """

    model: type[ArticleDocument] = ArticleDocument

    def set_extra_driver_options(self, options: object) -> None:
        """
        Set additional Selenium driver options for Medium crawling.

        Parameters
        ----------
        options : object
            Selenium webdriver options object.

        Returns
        -------
        None
        """
        options.add_argument(r"--profile-directory=Profile 2")  # type: ignore

    def extract(self, link: str, **kwargs: dict[str, Any]) -> None:
        """
        Extract article content from a Medium URL and save it to the database.

        Parameters
        ----------
        link : str
            The URL of the Medium article to extract.
        **kwargs : dict[str, Any]
            Additional keyword arguments, must contain 'user' object with
            id and full_name attributes.

        Returns
        -------
        None
        """
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Article already exists in the database: {link}")

            return

        logger.info(f"Starting scrapping Medium article: {link}")

        self.driver.get(link)
        self.scroll_page()

        soup: BeautifulSoup = BeautifulSoup(self.driver.page_source, "html.parser")
        title: list[Any] = soup.find_all("h1", class_="pw-post-title")
        subtitle: list[Any] = soup.find_all("h2", class_="pw-subtitle-paragraph")

        data: dict[str, str | None] = {
            "Title": title[0].string if title else None,
            "Subtitle": subtitle[0].string if subtitle else None,
            "Content": soup.get_text(),
        }

        self.driver.close()

        user = kwargs["user"]
        instance: ArticleDocument = self.model(
            platform="medium",
            content=data,
            link=link,
            author_id=user.id,  # type: ignore
            author_full_name=user.full_name,  # type: ignore
        )
        instance.save()

        logger.info(f"Successfully scraped and saved article: {link}")
