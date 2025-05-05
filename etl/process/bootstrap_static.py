from typing import Dict, List
from etl.fetch.bootstrap_static import fetch_bootstrap_static


def get_elements_from_team(team_id: int) -> List[int]:
    """
    Fetches the elements (players) from a specific team.

    Args:
        team_id (int): The ID of the team.

    Returns:
        List[int]: A list of player IDs in the team.

    Raises:
        ValueError: If team_id is not found in the data
    """
    # Fetch the latest bootstrap-static data
    raw_data: Dict[str, List[Dict[str, int]]] = fetch_bootstrap_static()
    # Extract elements data
    elements: List[Dict[str, int]] = raw_data.get("elements", [])

    # Filter elements by team ID
    team_elements: List[int] = [
        element['id'] for element in elements
        if element["team"] == team_id
    ]

    if not team_elements:
        raise ValueError(f"No elements found for team_id: {team_id}")

    return team_elements


if __name__ == '__main__':
    try:
        elements = get_elements_from_team(1)
        print(f"Elements in team 1: {elements}")
    except ValueError as e:
        print(f"Error: {str(e)}")
