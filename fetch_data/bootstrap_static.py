import logging
import requests
import polars as pl
from functools import lru_cache


class BootstrapStaticFetcher:
    """Fetches data from the Fantasy Premier League bootstrap-static
    endpoint."""

    URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

    def __init__(self, tables_to_extract=None):
        self.tables_to_extract = tables_to_extract or [
            "elements", "teams", "events", "element_types"
        ]

    def fetch(self):
        """Fetches the bootstrap-static data from the API."""
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

    def extract_tables(self, data):
        """Extracts specified top-level tables."""
        return {table: data.get(table, []) for table in self.tables_to_extract}

    def convert_table_to_polars(self, table_name, data):
        """Converts a table (list of dictionaries) to a Polars DataFrame."""
        if table_name not in self.tables_to_extract:
            raise ValueError(
                f"Table '{table_name}' is not in the list of extracted "
                "tables.")

        # Convert the table to Polars DataFrame
        try:
            return pl.DataFrame(data[table_name])
        except Exception as e:
            logging.error(
                f"Failed to convert table '{table_name}' to Polars DataFrame:"
                f" {e}")
            raise

    def run(self):
        """Fetches and extracts the tables."""
        data = self.fetch()
        return self.extract_tables(data)


@lru_cache(maxsize=None)
def __fetch_bootstrap_static_internal():
    """
    Retreive the data from bootstrap static and used cached data if it
    already exists.
    """
    bootstrap_static_fetcher = BootstrapStaticFetcher()
    return bootstrap_static_fetcher.run()


def fetch_bootstrap_static(force_refresh: bool = False):
    """
    Retreive the data from bootstrap static and used cached data if it
    already exists.
    """
    if force_refresh:
        __fetch_bootstrap_static_internal.cache_clear()
    return __fetch_bootstrap_static_internal()


if __name__ == "__main__":
    fetcher = BootstrapStaticFetcher()
    data = fetcher.fetch_data()
    print(data)  # For testing purposes
