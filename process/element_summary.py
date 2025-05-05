import logging
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from fetch import ElementSummaryFetcher
from fetch.bootstrap_static import fetch_bootstrap_static
from upload.storage import upload_json_to_gcs
from upload.bigquery import upload_element_summary_from_gcs_to_bigquery


def get_element_summary_for_teams(
        team_ids: List[int],
        element_ids: Optional[List[int]] = None
        ) -> Dict[str, Any]:
    """
    Fetch the element summary data for all players in the given teams.

    Args:
        team_ids (List[int]): List of team IDs to fetch player data for.
        element_ids (Optional[List[int]], optional): Specific player IDs to
            fetch within the specified teams.

    Returns:
        Dict[str, Any]: A dictionary containing the element summary data.
    """
    # Step 1: Fetch the latest bootstrap-static data
    raw_data: Dict[str, Any] = fetch_bootstrap_static()

    # Step 2: Extract elements data
    elements: List[Dict[str, Any]] = raw_data.get("elements", [])

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
        element_ids: Optional[List[int]] = None
        ) -> None:
    """
    Fetches element summaries for a single team and uploads to Cloud Storage.

    Args:
        team_id (int): The team ID.
        bucket_name (str): GCS bucket name.
        destination_folder (str): Folder path inside the bucket.
        element_ids (Optional[List[int]], optional): Specific element IDs to
            filter players.
    """
    try:
        logging.info(f"Fetching data for team {team_id}...")
        data: Dict[str, Any] = get_element_summary_for_teams(
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
                logging.info(
                    f"Uploading table {table_name} for "
                    f"team {team_id} to GCS at {blob_name}..."
                    "team {team_id} to GCS at {blob_name}..."
                )
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
    team_ids: List[int],
    bucket_name: str,
    destination_folder: str = 'element_summary',
    element_ids: Optional[List[int]] = None,
    max_workers: int = 5
) -> None:
    """
    Fetch and upload element summaries for multiple teams in parallel.

    Args:
        team_ids (List[int]): List of team IDs to process.
        bucket_name (str): GCS bucket name.
        destination_folder (str): Folder path inside the bucket.
        element_ids (Optional[List[int]], optional): Specific element IDs to
            filter players.
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


def fetch_and_upload_element_summary(
        project_id: str,
        bucket_name: str,
        dataset_id: str,
        destination_folder: str = 'element_summary',
        team_ids: Optional[List[int]] = None,
        element_ids: Optional[List[int]] = None,
        max_workers: int = 5
        ) -> None:
    """
    Fetch data from the element_summary endpoint and upload to BigQuery

    Args:
        project_id (str): GCP project ID
        bucket_name (str): GCS bucket name
        dataset_id (str): BigQuery dataset ID
        destination_folder (str): GCS destination folder
        team_ids (Optional[List[int]], optional): Specific team IDs to process
        element_ids (Optional[List[int]], optional): Specific element IDs to
            filter players
        max_workers (int): Number of threads to use for parallel processing
    """
    if not team_ids:
        bootstrap_static_data: Dict[str, Any] = fetch_bootstrap_static()
        teams: List[Dict[str, Any]] = bootstrap_static_data['teams']
        team_ids = [t['id'] for t in teams]

    logging.info(
        f"Fetching element summary data for teams: {team_ids} "
        "and uploading to GCS bucket: "
        f"{bucket_name} in folder: {destination_folder}"
    )
    fetch_and_upload_multiple_teams(
        team_ids=team_ids,
        bucket_name=bucket_name,
        destination_folder=destination_folder,
        element_ids=element_ids,
        max_workers=max_workers
    )

    tables = [
        'element_summary_fixtures',
        'element_summary_history',
        'element_summary_history_past'
    ]

    for table_id in tables:
        logging.info(f"Uploading table {table_id} to BigQuery...")
        upload_element_summary_from_gcs_to_bigquery(
            project_id=project_id,
            dataset_id=dataset_id,
            bucket_name=bucket_name,
            source_folder=destination_folder,
            table_id=table_id
        )


if __name__ == "__main__":
    import os
    import argparse
    from dotenv import load_dotenv
    from utils.string_manipulation import list_of_ints

    logging.basicConfig(
        level=logging.INFO,  # Change to DEBUG for verbose logs
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Upload data to BigQuery table.")
    parser.add_argument(
        "--team_ids",
        type=list_of_ints,
        default="1,2",
        help="The ID's of the teams to ingest"
    )
    parser.add_argument(
        "--element_ids",
        type=list_of_ints,
        default="1,2,28,29",
        help="The ID's of the players (elements) from the teams to ingest"
    )
    args = parser.parse_args()

    # team_ids = [1, 2]
    # element_ids = [1, 2, 28, 29]

    BUCKET = os.getenv("BUCKET_ID")
    PROJECT = os.getenv("PROJECT_ID")
    DATASET = os.getenv("DATASET_ID")

    fetch_and_upload_element_summary(
        project_id=PROJECT,
        bucket_name=BUCKET,
        dataset_id=DATASET,
        team_ids=args.team_ids,
        element_ids=args.element_ids,
        destination_folder='element_summary',
        max_workers=5
    )
