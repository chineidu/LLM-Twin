from typing import Any
from urllib.parse import urlparse

from loguru import logger
from tqdm import tqdm
from typing_extensions import Annotated
from zenml import get_step_context, step

from llm_engineering.application.crawlers.dispatcher import CrawlerDispatcher
from llm_engineering.domain.documents import UserDocument


@step
def crawl_links(
    user: UserDocument, links: list[str]
) -> Annotated[list[str], "crawled_links"]:
    """Crawl a list of links and extract information using appropriate crawlers.

    Parameters
    ----------
    user : UserDocument
        The user document containing user information.
    links : list[str]
        A list of URLs to crawl.

    Returns
    -------
    list[str]
        The list of processed links.
    """
    dispatcher: CrawlerDispatcher = (
        CrawlerDispatcher.build()
        .register_linkedin()
        .register_medium()
        .register_github()
    )

    logger.info(f"Starting to crawl {len(links)} link(s).")

    metadata: dict[str, dict[str, Any]] = {}
    successfull_crawls: int = 0
    for link in tqdm(links):
        successfull_crawl, crawled_domain = _crawl_link(dispatcher, link, user)
        successfull_crawls += successfull_crawl

        metadata = _add_to_metadata(metadata, crawled_domain, successfull_crawl)

    step_context = get_step_context()
    step_context.add_output_metadata(output_name="crawled_links", metadata=metadata)

    logger.info(f"Successfully crawled {successfull_crawls} / {len(links)} links.")

    return links


def _crawl_link(
    dispatcher: CrawlerDispatcher, link: str, user: UserDocument
) -> tuple[bool, str]:
    """Attempt to crawl a single link using the appropriate crawler.

    Parameters
    ----------
    dispatcher : CrawlerDispatcher
        The dispatcher instance that provides appropriate crawlers.
    link : str
        The URL to crawl.
    user : UserDocument
        The user document containing user information.

    Returns
    -------
    tuple[bool, str]
        A tuple containing (success_status, domain_name).
    """
    crawler = dispatcher.get_crawler(link)
    crawler_domain: str = urlparse(link).netloc

    try:
        crawler.extract(link=link, user=user)

        return (True, crawler_domain)
    except Exception as e:
        logger.error(f"An error occurred while crowling: {e!s}")

        return (False, crawler_domain)


def _add_to_metadata(
    metadata: dict[str, dict[str, Any]], domain: str, successful_crawl: bool
) -> dict[str, dict[str, Any]]:
    """Update metadata dictionary with crawling results for a domain.

    Parameters
    ----------
    metadata : dict[str, dict]
        The metadata dictionary to update.
    domain : str
        The domain name of the crawled URL.
    successful_crawl : bool
        Whether the crawl was successful.

    Returns
    -------
    dict[str, dict]
        The updated metadata dictionary.
    """
    if domain not in metadata:
        metadata[domain] = {}
    metadata[domain]["successful"] = (
        metadata.get(domain, {}).get("successful", 0) + successful_crawl
    )
    metadata[domain]["total"] = metadata.get(domain, {}).get("total", 0) + 1

    return metadata
