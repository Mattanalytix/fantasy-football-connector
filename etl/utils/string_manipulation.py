from typing import List


def list_of_ints(arg: str) -> List[int]:
    """
    Convert a comma-separated string of integers into a list of integers.

    Args:
        arg (str): A string containing comma-separated integers.

    Returns:
        List[int]: A list of integers parsed from the input string.

    Example:
        >>> list_of_ints("1,2,3")
        [1, 2, 3]
    """
    return list(map(int, arg.split(',')))
