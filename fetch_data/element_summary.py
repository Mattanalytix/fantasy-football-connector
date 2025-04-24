import logging
import aiohttp
import asyncio


class ElementSummaryFetcher:
    """Fetches data from the Fantasy Premier League element-summary endpoint in parallel."""
    
    BASE_URL = "https://fantasy.premierleague.com/api/element-summary/{}/"

    def __init__(self, player_ids):
        self.player_ids = player_ids
        logging.info(f"Initialized fetcher with {len(player_ids)} player IDs")

    async def fetch_player(self, session, player_id):
        """Fetches a single player's data asynchronously."""
        url = self.BASE_URL.format(player_id)
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    logging.debug(f"Fetched data for player {player_id}")
                    raw_data = await response.json()

                    # Inject element key into each subtable record
                    fixtures = [{'element': player_id, **f} for f in raw_data.get("fixtures", [])]
                    history = raw_data.get("history", [])
                    history_past = [{'element': player_id, **hp} for hp in raw_data.get("history_past", [])]

                    return {
                        "player_id": player_id,
                        "fixtures": fixtures,
                        "history": history,
                        "history_past": history_past
                    }
                else:
                    logging.error(f"HTTP {response.status} for player {player_id}")
                    return {
                        "player_id": player_id,
                        "fixtures": [],
                        "history": [],
                        "history_past": [],
                        "error": f"HTTP {response.status}"
                    }       
        except Exception as e:
            return {
                "player_id": player_id,
                "fixtures": [],
                "history": [],
                "history_past": [],
                "error": str(e)
            }

    async def fetch_all_players(self):
        """Fetches all players in parallel."""
        logging.info("Starting parallel fetch for players")
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_player(session, player_id) for player_id in self.player_ids]
            results = await asyncio.gather(*tasks)

        logging.info("Completed all fetches")
        return results

    def flatten_results(self, results):
        """Flattens the results into a single list."""
        all_fixtures = []
        all_history = []
        all_history_past = []
        errors = []

        for result in results:
            if 'error' in result:
                logging.warning(f"Adding error for player {result['player_id']} to errors table due to error: {result['error']}")
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

    def run(self):
        """Runs the async fetcher."""
        raw_results = asyncio.run(self.fetch_all_players())
        return self.flatten_results(raw_results)

# Example usage
if __name__ == "__main__":
    fetcher = ElementSummaryFetcher(player_ids=[1, 2, 3, 4, 5])
    data = fetcher.run()
    print(data)
