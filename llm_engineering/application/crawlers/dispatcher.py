import re
from urllib.parse import urlparse

from loguru import logger

from .base import BaseCrawler
from .custom_article import CustomArticleCrawler
from .github import GithubCrawler
from .linkedin import LinkedInCrawler
from .medium import MediumCrawler


class CrawlerDispatcher:
    """
    A dispatcher class that manages and routes URLs to appropriate web crawlers.

    Attributes
    ----------
    _crawlers : dict[str, type[BaseCrawler]]
        Dictionary mapping URL patterns to crawler classes.
    """

    def __init__(self) -> None:
        """
        Initialize the CrawlerDispatcher with an empty crawler dictionary.
        """
        self._crawlers: dict[str, type[BaseCrawler]] = {}

    @classmethod
    def build(cls) -> "CrawlerDispatcher":
        """
        Create and return a new instance of CrawlerDispatcher.

        Returns
        -------
        CrawlerDispatcher
            A new instance of the dispatcher.
        """
        dispatcher: CrawlerDispatcher = cls()
        return dispatcher

    def register_medium(self) -> "CrawlerDispatcher":
        """
        Register the Medium crawler for medium.com URLs.

        Returns
        -------
        CrawlerDispatcher
            The current dispatcher instance for method chaining.
        """
        self.register("https://medium.com", MediumCrawler)
        return self

    def register_linkedin(self) -> "CrawlerDispatcher":
        """
        Register the LinkedIn crawler for linkedin.com URLs.

        Returns
        -------
        CrawlerDispatcher
            The current dispatcher instance for method chaining.
        """
        self.register("https://linkedin.com", LinkedInCrawler)
        return self

    def register_github(self) -> "CrawlerDispatcher":
        """
        Register the GitHub crawler for github.com URLs.

        Returns
        -------
        CrawlerDispatcher
            The current dispatcher instance for method chaining.
        """
        self.register("https://github.com", GithubCrawler)
        return self

    def register(self, domain: str, crawler: type[BaseCrawler]) -> None:
        """
        Register a crawler for a specific domain.

        Parameters
        ----------
        domain : str
            The domain URL to register the crawler for.
        crawler : type[BaseCrawler]
            The crawler class to handle the domain.
        """
        parsed_domain: urlparse = urlparse(domain)  # type: ignore
        domain: str = parsed_domain.netloc  # type: ignore

        self._crawlers[r"https://(www\.)?{}/*".format(re.escape(domain))] = crawler

    def get_crawler(self, url: str) -> BaseCrawler:
        """
        Get the appropriate crawler instance for a given URL.

        Parameters
        ----------
        url : str
            The URL to get a crawler for.

        Returns
        -------
        BaseCrawler
            An instance of the appropriate crawler for the URL,
            or CustomArticleCrawler if no specific crawler is found.
        """
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()
        else:
            logger.warning(
                f"No crawler found for {url}. Defaulting to CustomArticleCrawler."
            )
            return CustomArticleCrawler()
