import time
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger
from selenium.webdriver.common.by import By

from llm_engineering.domain.documents import PostDocument
from llm_engineering.domain.exceptions import ImproperlyConfiguredException
from llm_engineering.settings import settings
from .base import BaseSeleniumCrawler


class LinkedInCrawler(BaseSeleniumCrawler):
    """LinkedIn crawler for extracting profile data and posts.

    Parameters
    ----------
    scroll_limit : int, default=5
        Number of times to scroll the page
    is_deprecated : bool, default=True
        Flag indicating if the crawler is using deprecated methods

    Attributes
    ----------
    model : PostDocument
        Document model for storing posts
    """

    model = PostDocument

    def __init__(self, scroll_limit: int = 5, is_deprecated: bool = True) -> None:
        super().__init__()
        self._is_deprecated = is_deprecated

    def set_extra_driver_options(self, options: Any) -> None:
        """Set additional Selenium driver options.

        Parameters
        ----------
        options : Any
            Selenium webdriver options object
        """
        options.add_experimental_option("detach", True)

    def login(self) -> None:
        """Perform LinkedIn login using credentials from settings.

        Raises
        ------
        DeprecationWarning
            If the crawler is marked as deprecated
        ImproperlyConfiguredException
            If LinkedIn credentials are not configured
        """
        if self._is_deprecated:
            raise DeprecationWarning(
                "LinkedIn has updated its security measures, the login() method "
                "is no longer supported."
            )
        self.driver.get("https://www.linkedin.com/login")
        if not settings.LINKEDIN_USERNAME or not settings.LINKEDIN_PASSWORD:
            raise ImproperlyConfiguredException(
                "Please set your LinkedIn credentials: "
                "LINKEDIN_USERNAME and LINKEDIN_PASSWORD in your .env file."
            )
        self.driver.find_element(By.ID, "username").send_keys(
            settings.LINKEDIN_USERNAME
        )
        self.driver.find_element(By.ID, "password").send_keys(
            settings.LINKEDIN_PASSWORD
        )
        self.driver.find_element(
            By.CSS_SELECTOR, ".login__form_action_container button"
        ).click()

    def extract(self, link: str, **kwargs: dict[str, Any]) -> None:
        """Extract posts and profile data from a LinkedIn profile.

        Parameters
        ----------
        link : str
            LinkedIn profile URL
        **kwargs : dict[str, Any]
            Additional keyword arguments including user information

        Raises
        ------
        DeprecationWarning
            If the crawler is marked as deprecated
        """
        if self._is_deprecated:
            raise DeprecationWarning(
                "LinkedIn has updated its feed structure, the extract() method "
                "is no longer supported."
            )
        if self.model.link is not None:
            old_model = self.model.find(link=link)
            if old_model is not None:
                logger.info(f"Post already exists in the database: {link}")
                return

        logger.info(f"Extracting post: {link}")
        self.login()

        soup = self._get_page_content(link)
        data: dict[str, Any] = {  # noqa: F841
            "Name": self._scrape_section(soup, "hi", class_="text-heading-xlarge"),  # type: ignore
            "About": self._scrape_section(soup, "div", class_="display-flex ph5 pv3"),  # type: ignore
            "Main Page": self._scrape_section(soup, "div", {"id": "main-content"}),  # type: ignore
            "Experience": self._scrape_experience(link),
            "Education": self._scrape_education(link),
        }
        self.driver.get(link)
        time.sleep(5)
        button = self.driver.find_element(
            By.CSS_SELECTOR,
            ".app-aware-link.profile-creator-shared-content-view__footer-action",
        )
        button.click()

        self.scroll_page()
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        post_elements = soup.find_all(
            "div",
            class_="update-components-text relative update-components-update-v2__commentary",
        )
        buttons = soup.find_all("button", class_="update-components-image__image-link")
        post_images = self._extract_image_urls(buttons)
        posts = self._extract_posts(post_elements, post_images)
        logger.info(f"Found {len(posts)} posts for profile: {link}")

        self.driver.close()

        user = kwargs.get("user")
        self.model.bulk_insert(
            [
                PostDocument(
                    platform="LinkedIn",
                    content=post,
                    author_id=user.id,  # type: ignore
                    author_full_name=user.full_name,  # type: ignore
                )
                for post in posts
            ]
        )
        logger.info(f"Finnished extracting posts for profile: {link}")

    def _scrape_section(
        self, soup: BeautifulSoup, *args, **kwargs: dict[str, Any]
    ) -> str:
        """Scrape text content from a specific section of the page.

        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
        *args : tuple
            Positional arguments for BeautifulSoup find method
        **kwargs : dict[str, Any]
            Keyword arguments for BeautifulSoup find method

        Returns
        -------
        str
            Extracted text content or empty string if section not found
        """
        parent_div = soup.find(*args, **kwargs)
        return parent_div.get_text(strip=True) if parent_div else ""

    def _extract_image_urls(self, buttons: list[Tag]) -> dict[str, str]:
        """Extract image URLs from post buttons.

        Parameters
        ----------
        buttons : list[Tag]
            List of BeautifulSoup Tag objects containing image buttons

        Returns
        -------
        dict[str, str]
            Dictionary mapping post indices to image URLs
        """
        post_images: dict[str, str] = {}
        for index, button in enumerate(buttons):
            img_tag = button.find("img")
            if img_tag and "src" in img_tag.attrs:
                post_images[f"Post {index}"] = img_tag["src"]
            else:
                logger.warning(f"No image found for button {index}")

        return post_images

    def _get_page_content(self, url: str) -> BeautifulSoup:
        """Fetch and parse page content.

        Parameters
        ----------
        url : str
            URL to fetch content from

        Returns
        -------
        BeautifulSoup
            Parsed HTML content
        """
        self.driver.get(url)
        time.sleep(5)
        return BeautifulSoup(self.driver.page_source, "html.parser")

    def _extract_posts(
        self, post_elements: list[Tag], post_images: dict[str, str]
    ) -> dict[str, Any]:
        """Extract post content and associated images.

        Parameters
        ----------
        post_elements : list[Tag]
            List of BeautifulSoup Tag objects containing post content
        post_images : dict[str, str]
            Dictionary mapping post indices to image URLs

        Returns
        -------
        dict[str, Any]
            Dictionary containing post text and associated images
        """
        posts_data: dict[str, Any] = {}
        for index, post_element in enumerate(post_elements):
            post_text = post_element.get_text(strip=True, separator="\n")
            post_data = {"text": post_text}
            if f"Post {index}" in post_images:
                post_data["image"] = post_images[f"Post {index}"]
            posts_data[f"Post {index}"] = post_data

        return posts_data

    def _scrape_experience(self, profile_url: str) -> str:
        """Scrape the Experience section of the LinkedIn profile.

        Parameters
        ----------
        profile_url : str
            Base URL of the LinkedIn profile

        Returns
        -------
        str
            Extracted experience content or empty string if section not found
        """
        self.driver.get(profile_url + "/details/experience/")
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        experience_content = soup.find("section", {"id": "experience-section"})
        return experience_content.get_text(strip=True) if experience_content else ""

    def _scrape_education(self, profile_url: str) -> str:
        """Scrape the Education section of the LinkedIn profile.

        Parameters
        ----------
        profile_url : str
            Base URL of the LinkedIn profile

        Returns
        -------
        str
            Extracted education content or empty string if section not found
        """
        self.driver.get(profile_url + "/details/education/")
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        education_content = soup.find("section", {"id": "education-section"})
        return education_content.get_text(strip=True) if education_content else ""
