import logging
import requests
from typing import List, Dict, Optional, Any
from functools import lru_cache


class BootstrapStaticFetcher:
    """
    Fetches data from the Fantasy Premier League bootstrap-static endpoint.

    Attributes:
        URL (str): The API endpoint URL for bootstrap-static data
        tables_to_extract (List[str]): List of table names to extract from the
            response
    """

    URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

    def __init__(self, tables_to_extract: Optional[List[str]] = None) -> None:
        """
        Initialize the BootstrapStaticFetcher.

        Args:
            tables_to_extract (Optional[List[str]]): List of table names to
                extract.
                Defaults to ['elements', 'teams', 'events', 'element_types']
                if not provided.
        """
        self.tables_to_extract = tables_to_extract or [
            "elements", "teams", "events", "element_types"
        ]

    def fetch(self) -> Dict[str, Any]:
        """
        Fetches the bootstrap-static data from the API.

        Returns:
            Dict[str, Any]: The JSON response data from the API

        Raises:
            requests.exceptions.RequestException: If there's an error making
            the request
        """
        try:
            response = requests.get(self.URL)
            if response.status_code == 200:
                return response.json()
            else:
                if response.status_code == 503:
                    logging.error("Service Unavailable (503) - "
                                  "The game may be updating.")
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred: {e}")
            raise

    def extract_tables(self, data: Dict[str, Any]) -> Dict[str, List[Any]]:
        """
        Extracts specified top-level tables from the API response.

        Args:
            data (Dict[str, Any]): The full API response data

        Returns:
            Dict[str, List[Any]]: Dictionary containing only the requested
            tables
        """
        return {table: data.get(table, []) for table in self.tables_to_extract}

    def run(self) -> Dict[str, List[Any]]:
        """
        Fetches and extracts the specified tables from the API.

        Returns:
            Dict[str, List[Any]]: Dictionary containing the extracted tables
        """
        data = self.fetch()
        return self.extract_tables(data)


@lru_cache(maxsize=None)
def __fetch_bootstrap_static_internal() -> Dict[str, List[Any]]:
    """
    Retrieve the data from bootstrap static using cached data if available.

    Returns:
        Dict[str, List[Any]]: Dictionary containing the extracted tables
    """
    bootstrap_static_fetcher = BootstrapStaticFetcher()
    return bootstrap_static_fetcher.run()


def fetch_bootstrap_static(
        force_refresh: bool = False
        ) -> Dict[str, List[Any]]:
    """
    Retrieve the data from bootstrap static, using cached data if available.

    Args:
        force_refresh (bool): If True, clears the cache and fetches fresh data

    Returns:
        Dict[str, List[Any]]: Dictionary containing the extracted tables
    """
    if force_refresh:
        __fetch_bootstrap_static_internal.cache_clear()
    return __fetch_bootstrap_static_internal()


if __name__ == "__main__":
    fetcher = BootstrapStaticFetcher()
    data = fetcher.fetch()
    print(data)  # For testing purposes
