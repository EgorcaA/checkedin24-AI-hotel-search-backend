import json
import unittest

import pandas as pd

from .process_hotels import (
    filter_and_rank_hotels,
    find_matching_hotels,
    normalize_value,
)


class TestProcessHotels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Sample test data
        cls.test_hotels = pd.DataFrame(
            {
                "hotel_name": ["Test Hotel 1", "Test Hotel 2", "Test Hotel 3"],
                "pricepernight": [100, 200, 300],
                "rating": [4.5, 4.0, 3.5],
                "ratingscount": [1000, 500, 100],
                "starcategory": [5, 4, 3],
                "distancetocity": [1, 2, 5],
                "distancetounderground": [0.2, 0.5, 1],
                "distancetobeach": [0.1, 1, 5],
                "distancetoairport": [10, 15, 20],
                "popular_location_rank": [5, 15, 30],
                "wifi": [True, True, False],
                "swimming_pool": [True, False, True],
                "breakfast": [True, True, True],
                "mealtype": ["breakfast", "all_inclusive", "only_stay"],
                "roomcategory": [
                    "Deluxe Double Room",
                    "Standard Double Room",
                    "Economy Double Room",
                ],
            }
        )

    def test_normalize_value(self):
        # Test rating normalization
        self.assertAlmostEqual(normalize_value("rating", 4.5), 0.9)
        self.assertAlmostEqual(normalize_value("rating", 5.0), 1.0)

        # Test star category normalization
        self.assertAlmostEqual(normalize_value("starcategory", 5), 1.0)
        self.assertAlmostEqual(normalize_value("starcategory", 3), 0.6)

        # Test distance normalization (inverse relationship)
        self.assertTrue(
            normalize_value("distancetocity", 1) > normalize_value("distancetocity", 5)
        )

        # Test price normalization (inverse relationship)
        self.assertTrue(
            normalize_value("pricepernight", 100)
            > normalize_value("pricepernight", 200)
        )

        # Test unknown field
        self.assertEqual(normalize_value("unknown_field", 100), 0.0)

    def test_filter_and_rank_hotels(self):
        test_preferences = {
            "fields": {
                "max_price_usd": {"value": 250, "crucial": True, "weight": 5},
                "min_rating": {"value": 4.0, "crucial": True, "weight": 4},
            },
            "amenities": {
                "wifi": {"crucial": True, "weight": 3},
                "swimming_pool": {"crucial": False, "weight": 2},
            },
            "chooseparameters": {
                "mealtype": {
                    "dict": {"breakfast": 3, "all_inclusive": 5, "only_stay": 1},
                    "crucial": False,
                    "weight": 2,
                }
            },
        }

        results = filter_and_rank_hotels(self.test_hotels, test_preferences)

        # Check if filtering worked
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(results["pricepernight"] <= 250))
        self.assertTrue(all(results["rating"] >= 4.0))
        self.assertTrue(all(results["wifi"] == True))

        # Check if sorting worked (match_score should be descending)
        self.assertTrue(results["match_score"].is_monotonic_decreasing)

    def test_find_matching_hotels(self):
        # This test requires mocking the OpenAI client
        # For now, we'll just test the basic structure
        test_query = "I want a hotel with wifi and breakfast under $200"

        _, results = find_matching_hotels(test_query, self.test_hotels)
        print(results)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, pd.DataFrame)
        self.assertTrue("match_score" in results.columns)


if __name__ == "__main__":
    unittest.main()
