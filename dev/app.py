def find_matching_hotels(
    query: str, hotels: dict[str, dict[str, object]]
) -> list[str] | None:
    """
    Find matching hotels based on the given query.

    Args:
        query (str): The search query from the user.
        hotels (dict[str, dict[str, object]]): Dictionary containing hotel information.
            Format: {
                "hotel_name": {
                    "name": str,
                    "rating": float,
                    "distance_to_beach": float,
                    ...
                },
                ...
            }

    Returns:
        list[str] | None: List of hotel_names that match the query, or None if the query is not hotel related.
    """
    # TODO: Implement the logic to find matching hotels based on the query.
