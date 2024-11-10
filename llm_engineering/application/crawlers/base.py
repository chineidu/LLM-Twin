import time
from abc import ABC, abstractmethod
from tempfile import mkdtemp

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from llm_engineering.domain.documents import NoSQLBaseDocument


# Check if the current version of chromedriver exists and 
# install otherwise download it automatically.
chromedriver_autoinstaller.install()


class BaseCrawler(ABC):
    """
    Abstract base class for web crawlers.

    Attributes
    ----------
    model : type[NoSQLBaseDocument]
        The document model class for storing crawled data.
    """
    model: type[NoSQLBaseDocument]

    @abstractmethod
    def extract(self, link: str, **kwargs: dict) -> None:
        """
        Extract data from the given link.

        Parameters
        ----------
        link : str
            The URL to extract data from.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        None
        """
        pass

    class BaseSeleniumCrawler(BaseCrawler, ABC):
        """
        Base class for Selenium-based web crawlers.

        Parameters
        ----------
        scroll_limit : int, optional
            Maximum number of scroll operations, by default 5

        Attributes
        ----------
        scroll_limit : int
            Maximum number of scroll operations
        driver : webdriver.Chrome
            Chrome WebDriver instance
        """
        def __init__(self, scroll_limit: int = 5) -> None:
            options = webdriver.ChromeOptions()

            options.add_argument("--no-sandbox")
            options.add_argument("--headless=new")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--log-level=3")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-certain-errors")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument(f"--user-data-dir={mkdtemp()}")
            options.add_argument(f"--data-path={mkdtemp()}")
            options.add_argument(f"--disk-cache-dir={mkdtemp()}")
            options.add_argument("--remote-debugging-port=9226")

            options.set_extra_driver_options(options)

            self.scroll_limit = scroll_limit
            self.driver = webdriver.Chrome(options=options)

        def set_extra_driver_options(self, options: Options) -> None:
            """
            Set additional Chrome driver options.

            Parameters
            ----------
            options : Options
                Chrome driver options instance.

            Returns
            -------
            None
            """
            pass

        def login(self) -> None:
            """
            Perform login operation.

            Returns
            -------
            None
            """
            pass

        def scroll_page(self) -> None:
            """
            Scroll the page to load dynamic content.

            Returns
            -------
            None
            """
            current_scroll: int = 0
            last_height: int = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            while True:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(5)
                new_height: int = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_height == last_height or (
                    self.scroll_limit and current_scroll >= self.scroll_limit
                ):
                    break
                last_height = new_height
                current_scroll += 1