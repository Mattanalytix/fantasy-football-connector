import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from fetch_data import BootstrapStaticFetcher, ElementSummaryFetcher
from upload.storage import upload_json_to_gcs


def get_element_summary_for_teams(
        team_ids: list,
        element_ids: list = None
        ) -> dict:
    """
    Fetch the element summary data for all players in the given teams.

    Args:
        team_ids (list): List of team IDs to fetch player data for.
        element_ids (list, optional): Specific player IDs to fetch within the
            specified teams.

    Returns:
        dict: A dictionary containing the element summary data.
    """
    # Step 1: Fetch the latest bootstrap-static data
    bootstrap_static_fetcher = BootstrapStaticFetcher()
    raw_data = bootstrap_static_fetcher.fetch()

    # Step 2: Extract elements data
    elements = raw_data.get("elements", [])

    # Step 3: Create a mapping of player IDs to their team IDs
    player_team_map = {element["id"]: element["team"] for element in elements}

    if element_ids is None:
        # Filter player IDs by matching team IDs
        filtered_player_ids = [
            player_id for player_id, team_id in player_team_map.items()
            if team_id in team_ids
        ]
    else:
        # Filter element_ids to make sure they exist and belong to the
        # specified teams
        filtered_player_ids = [
            player_id for player_id in element_ids
            if player_id in player_team_map
            and player_team_map[player_id] in team_ids
        ]

        invalid_element_ids = [
            player_id for player_id in element_ids
            if player_id not in player_team_map
            or player_team_map[player_id] not in team_ids
        ]

        if invalid_element_ids:
            logging.warning(
                "The following provided elements are not in the specified"
                " teams: %s",
                invalid_element_ids
            )

    # Step 4: Fetch element summaries for the selected player IDs
    logging.info(
        f"Fetching element summaries for {len(filtered_player_ids)}"
        " players...")
    element_summary_fetcher = ElementSummaryFetcher(
        player_ids=filtered_player_ids)
    return element_summary_fetcher.run()


def fetch_and_upload_team_summary(
        team_id: int,
        bucket_name: str,
        destination_folder: str = 'element_summary',
        element_ids: list = None
        ) -> None:
    """
    Fetches element summaries for a single team and uploads to Cloud Storage.

    Args:
        team_id (int): The team ID.
        element_ids (list): Full list of element_ids from bootstrap-static.
        bucket_name (str): GCS bucket name.
        destination_folder (str): Folder path inside the bucket.
    """
    try:
        logging.info(f"Fetching data for team {team_id}...")
        data = get_element_summary_for_teams(
            team_ids=[team_id],
            element_ids=element_ids
        )

        if not data:
            logging.warning(f"No data found for team {team_id}."
                            " Skipping upload.")
            return

        # Define GCS object name (e.g., "element_summary/team_1.json")
        for table_name, table_data in data.items():
            if table_data:
                file_name = f"element_summary_{table_name}_{team_id}.json"
                blob_name = f"{destination_folder}/{file_name}"

                # Upload to GCS
                upload_json_to_gcs(
                    bucket_name=bucket_name,
                    blob_name=blob_name,
                    data=table_data
                )

                logging.info(f"Uploaded table {table_name} for"
                             f" team {team_id} to GCS at {blob_name}.")

    except Exception as exc:
        logging.error(f"Error processing team {team_id}: {exc}")


def fetch_and_upload_multiple_teams(
    team_ids: list,
    bucket_name: str,
    destination_folder: str = 'element_summary',
    element_ids: list = None,
    max_workers: int = 5
) -> None:
    """
    Fetch and upload element summaries for multiple teams in parallel.

    Args:
        team_ids (list): List of team IDs to process.
        bucket_name (str): GCS bucket name.
        destination_folder (str): Folder path inside the bucket.
        element_ids (list, optional): Specific element IDs to filter players.
        max_workers (int): Number of threads to use.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_team = {
            executor.submit(
                fetch_and_upload_team_summary,
                team_id=team_id,
                bucket_name=bucket_name,
                destination_folder=destination_folder,
                element_ids=element_ids
            ): team_id for team_id in team_ids
        }

        for future in as_completed(future_to_team):
            team_id = future_to_team[future]
            try:
                future.result()
                logging.info(f"Finished processing team {team_id}.")
            except Exception as exc:
                logging.error(f"Team {team_id} generated an exception: {exc}")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    logging.basicConfig(
        level=logging.INFO,  # Change to DEBUG for verbose logs
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    load_dotenv()
    test_team_ids = [1, 2]
    test_team_id = 1
    test_element_ids = [1, 2, 28, 29]

    BUCKET = os.getenv("BUCKET_ID")

    fetch_and_upload_multiple_teams(
        team_ids=test_team_ids,
        bucket_name=BUCKET,
        destination_folder='element_summary',
        element_ids=test_element_ids,
        max_workers=5
    )
