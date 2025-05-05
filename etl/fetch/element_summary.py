import logging
import aiohttp
import asyncio
from typing import List, Dict, Any
from aiohttp import ClientSession


class ElementSummaryFetcher:
    """
    Fetches data from the Fantasy Premier League element-summary endpoint in
    parallel.

    Attributes:
        BASE_URL (str): The base URL template for element-summary endpoints
        player_ids (List[int]): List of player IDs to fetch data for
    """

    BASE_URL = "https://fantasy.premierleague.com/api/element-summary/{}/"

    def __init__(self, player_ids: List[int]) -> None:
        """
        Initialize the ElementSummaryFetcher.

        Args:
            player_ids (List[int]): List of player IDs to fetch data for
        """
        self.player_ids = player_ids
        logging.info(f"Initialized fetcher with {len(player_ids)} player IDs")

    async def fetch_player(self,
                           session: ClientSession,
                           player_id: int
                           ) -> Dict[str, Any]:
        """
        Fetches a single player's data asynchronously.

        Args:
            session (ClientSession): aiohttp client session for making requests
            player_id (int): ID of the player to fetch data for

        Returns:
            Dict[str, Any]: Dictionary containing player data including:
                - player_id: The player's ID
                - fixtures: List of fixture data with element key injected
                - history: List of history data with element key injected
                - history_past: List of past history data with element key
                    injected
                - error (optional): Error message if the request failed
        """
        url = self.BASE_URL.format(player_id)
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    logging.debug(f"Fetched data for player {player_id}")
                    raw_data = await response.json()

                    # Inject element key into each subtable record
                    fixtures = [{'element': player_id, 'data': f}
                                for f in raw_data.get("fixtures", [])]
                    history = [{'element': player_id, 'data': f}
                               for f in raw_data.get("history", [])]
                    history_past = [{'element': player_id, 'data': hp}
                                    for hp in raw_data.get("history_past", [])]

                    return {
                        "player_id": player_id,
                        "fixtures": fixtures,
                        "history": history,
                        "history_past": history_past
                    }
                else:
                    logging.error(
                        f"HTTP {response.status} for player {player_id}")
                    return {
                        "player_id": player_id,
                        "fixtures": [],
                        "history": [],
                        "history_past": [],
                        "error": f"HTTP {response.status}"
                    }

        except Exception as e:
            logging.error(f"Error fetching player {player_id}: {str(e)}")
            return {
                "player_id": player_id,
                "fixtures": [],
                "history": [],
                "history_past": [],
                "error": str(e)
            }

    async def fetch_all_players(self) -> List[Dict[str, Any]]:
        """
        Fetches all players in parallel using asyncio.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing player data
        """
        logging.info("Starting parallel fetch for players")
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_player(session, player_id)
                     for player_id in self.player_ids]
            results = await asyncio.gather(*tasks)

        logging.info("Completed all fetches")
        return results

    def flatten_results(
            self,
            results: List[Dict[str, Any]]
            ) -> Dict[str, List[Any]]:
        """
        Flattens the results into a single dictionary with separate lists for
        each data type.

        Args:
            results (List[Dict[str, Any]]): List of player data dictionaries

        Returns:
            Dict[str, List[Any]]: Dictionary containing:
                - fixtures: List of all fixture data
                - history: List of all history data
                - history_past: List of all past history data
                - errors: List of any errors that occurred during fetching
        """
        all_fixtures = []
        all_history = []
        all_history_past = []
        errors = []

        for result in results:
            if 'error' in result:
                logging.warning(
                    f"Adding error for player {result['player_id']}"
                    f" to errors table due to error: {result['error']}")
                errors.append({
                    "player_id": result.get("player_id"),
                    "error": result.get("error")
                })
                continue

            all_fixtures.extend(result.get("fixtures", []))
            all_history.extend(result.get("history", []))
            all_history_past.extend(result.get("history_past", []))

        return {
            "fixtures": all_fixtures,
            "history": all_history,
            "history_past": all_history_past,
            "errors": errors
        }

    def run(self) -> Dict[str, List[Any]]:
        """
        Runs the async fetcher and returns flattened results.

        Returns:
            Dict[str, List[Any]]: Dictionary containing all fetched data
        """
        raw_results = asyncio.run(self.fetch_all_players())
        return self.flatten_results(raw_results)


# Example usage
if __name__ == "__main__":
    fetcher = ElementSummaryFetcher(player_ids=[1, 2, 3, 4, 5])
    data = fetcher.run()
    print(data['history'][0].keys())
