import os
import shutil
import subprocess
import tempfile
from typing import Any

from loguru import logger

from llm_engineering.domain.documents import RepositoryDocument
from .base import BaseCrawler


class GithubCrawler(BaseCrawler):
    """
    A crawler for extracting content from GitHub repositories.

    Attributes
    ----------
    model : type
        The document model class used for storing repository data.
    ignore : tuple[str, ...]
        File and directory extensions to ignore during crawling.
    """

    model = RepositoryDocument

    def __init__(
        self, ignore: tuple[str, ...] = (".git", ".toml", ".lock", ".png")
    ) -> None:
        """
        Initialize the GitHub crawler.

        Parameters
        ----------
        ignore : tuple[str, ...]
            File and directory extensions to ignore during crawling.
            Default is (".git", ".toml", ".lock", ".png").

        Returns
        -------
        None
        """
        super().__init__()
        self.ignore = ignore

    def extract(self, link: str, **kwargs: dict[str, Any]) -> None:
        """
        Extract content from a GitHub repository.

        Parameters
        ----------
        link : str
            The URL of the GitHub repository to crawl.
        **kwargs : dict[str, Any]
            Additional keyword arguments.
            Expected to contain 'user' with attributes 'id' and 'full_name'.

        Returns
        -------
        None

        Notes
        -----
        Creates a RepositoryDocument instance with the following structure:
        - content: dict[str, str] mapping file paths to their contents
        - name: str, repository name
        - link: str, repository URL
        - platform: str, fixed as "GitHub"
        - author_id: Any, from user.id
        - author_full_name: str, from user.full_name
        """
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Repository already exists in the database: {link}")
            return

        logger.info(f"Extracting GitHub repository: {link}")

        repo_name: str = link.rstrip("/").split("/")[-1]
        local_temp: str = tempfile.mkdtemp()

        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])
            repo_path: str = os.path.join(local_temp, os.listdir(local_temp)[0])

            tree: dict[str, str] = {}
            for root, _, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lsplit("/")  # type: ignore
                if dir.startswith(self.ignore):
                    continue

                for file in files:
                    if file.endswith(self.ignore):
                        continue
                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        tree[file_path] = f.read().replace(" ", "")

            user = kwargs.get("user")
            instance = self.model(
                content=tree,
                name=repo_name,
                link=link,
                platform="GitHub",
                author_id=user.id,  # type: ignore
                author_full_name=user.full_name,  # type: ignore
            )
            instance.save()
        except Exception:
            raise
        finally:
            shutil.rmtree(local_temp)

        logger.info(f"Finished extracting documents from GitHub repository: {link}")
