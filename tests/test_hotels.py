from tests.conftest import client


def test_get_hotels_no_prompt(client):
    """Test that the endpoint returns all hotels when no prompt is provided"""
    response = client.get("/api/hotels")
    assert response.status_code == 200
    data = response.json()
    assert "hotels" in data
    assert "user_preferences" in data
    assert isinstance(data["hotels"], list)
    assert len(data["hotels"]) > 0


def test_get_hotels_with_prompt(client):
    """Test that the endpoint returns filtered hotels when a prompt is provided"""
    response = client.get("/api/hotels?prompt=test")
    assert response.status_code == 200
    data = response.json()
    assert "hotels" in data
    assert "user_preferences" in data
    assert isinstance(data["hotels"], list)


# def test_get_hotels_empty_result(client):
#     """Test that the endpoint returns empty list when no hotels match the prompt"""
#     response = client.get("/api/hotels?prompt=nonexistenthotel123")
#     assert response.status_code == 200
#     data = response.json()
#     assert "hotels" in data
#     assert "user_preferences" in data
#     assert isinstance(data["hotels"], list)
#     assert len(data["hotels"]) == 0


def test_hotel_schema(client):
    """Test that returned hotels have the correct schema"""
    response = client.get("/api/hotels")
    assert response.status_code == 200
    data = response.json()
    assert "hotels" in data
    assert "user_preferences" in data

    # Check that each hotel has required fields
    for hotel in data["hotels"]:
        assert "hotel_name" in hotel
        assert "amenities" in hotel
        assert isinstance(hotel["amenities"], list)
