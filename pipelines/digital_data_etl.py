from zenml import pipeline
from steps.etl import crawl_links, get_or_create_user


@pipeline
def digital_data_etl(
    user_full_name: str,
    links: list[str],
) -> str:
    """Execute the digital data ETL pipeline.

    Parameters
    ----------
    user_full_name : str
        The full name of the user to create or retrieve.
    links : list[str]
        A list of URLs to crawl and process.

    Returns
    -------
    str
        The invocation ID of the last executed step.
    """
    user = get_or_create_user(user_full_name=user_full_name)  # type: ignore
    last_step = crawl_links(user=user, links=links)  # type: ignore

    return last_step.invocation_id
