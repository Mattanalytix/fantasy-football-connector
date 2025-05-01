from fetch.bootstrap_static import fetch_bootstrap_static


def get_elements_from_team(
        team_id: int
        ) -> list:
    """
    Fetches the elements (players) from a specific team.
    Args:
        team_id (int): The ID of the team.
    Returns:
        list: A list of elements (players) in the team.
    """
    # Fetch the latest bootstrap-static data
    raw_data = fetch_bootstrap_static()
    # Extract elements data
    elements = raw_data.get("elements", [])
    # Filter elements by team ID
    team_elements = [
        element['id'] for element in elements
        if element["team"] == team_id
    ]
    return team_elements


if __name__ == '__main__':
    elements = get_elements_from_team()
    print(f"Elements in team 1: {elements}")
