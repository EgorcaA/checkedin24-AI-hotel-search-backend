import re

from dotenv import load_dotenv
from openai import OpenAI

from .params import amenities

load_dotenv()
import os

import pandas as pd

# print(os.getenv("OPENAI_API_KEY"))  # should print your key

client = OpenAI()
import json

SYSTEM_PROMPT = (
    f"""
You are an intelligent assistant helping to extract structured hotel preferences from a free-form customer request. Follow these steps precisely and return only a JSON object.

STEP 1: Extract only the relevant **fields**, **chooseparameters** and **amenities** mentioned or implied in the customer's request.
Do not create your own.

STEP 2: For each selected **field** , **chooseparameters** or **amenity**, return:
- A value.
- Whether it is **crucial** (True/False) — i.e., is it a must-have?
- A **weight** from 1 to 5 indicating how important it is (5 = most important).
- List also 5-10 non-crucial fields and amenities.

STEP 3: If the query is unrelated to hotels, return `null`.

---

### FIELD MAPPINGS

Return values as follows:

- `hotel_name`, `clusterchain`, `clusterbrand`, `clustersubbrand`: return as strings if mentioned.

**Price (`pricepernight`)**
- "cheap" → `max_price_usd` ≈ 80
- "affordable" → `max_price_usd` ≈ 150
- "mid-range" → `max_price_usd` ≈ 200
- "expensive" → `min_price_usd` ≈ 250

**Rating**
- "highly rated", "excellent" → `min_rating` ≈ 4.5
- "good", "decent" → `min_rating` ≈ 4.0
- "okay" → `min_rating` ≈ 3.5

**Ratings Count**
- "a lot of reviews" → `min_ratingscount` ≈ 1000
- "some reviews", "decent amount" → `min_ratingscount` ≈ 100

**Star Category**
- "standard", "good" → 3
- "upscale", "high quality" → 4
- "luxury", "5-star" → 5


**Distances**
- `max_distancetocity`:
  - "in the city center" → 0–1 km
  - "near center" → 1–3 km
  - "not far from city" → 3–6 km
  - "quiet area" → >6 km

- `max_distancetounderground`:
  - "right by metro" → 0–100 m
  - "near metro" → 100–400 m
  - "walkable to metro" → 400–800 m
  - "public transport accessible" → ≤1.5 km

- `max_distancetobeach`:
  - "beachfront" → 0–50 m
  - "near the beach" → 50–500 m
  - "short ride to beach" → 0.5–2 km
  - "not far from beach" → 2–5 km

- `max_distancetoairport`:
  - "near airport" → 0–5 km
  - "short drive to airport" → 5–15 km
  - "not far from airport" → 15–30 km
  - "remote from airport" → >30 km

- `max_popular_location_rank`:
  - "top location" → 1–10
  - "popular area" → 11–30
  - "well-located" → 31–60
  - "quiet area" → 61–100


---
### CHOOSEPARAMETERS
Set weights 0–5 to variants
Return dict of all the partially matching variants with weights if CHOOSEPARAMETER is mentioned.

**Meal Type** (`mealtype`):
[all_inclusive, breakfast, half_board, only_stay].

**Room Category** (`roomcategory`):
[Standard Double Room, Economy Shared Room, Economy Double Room, Standard Single Room, Superior Double Room, Standard Family Room, Comfort Double Room, Comfort Studio, Studio, Bed in a Dormitory, Deluxe Double Room, Business Double Room, Standard Shared Room, Other Room Category]


### AMENITIES
List of amenities to check and weight if mentioned or implied: """
    + f"{amenities}"
    + """
---

### OUTPUT FORMAT

Return as a single JSON object:

```json
{
  "fields": {
    "min_price_usd": { "value": 100, "crucial": true, "weight": 5 },
    "max_price_usd": { "value": 200, "crucial": false, "weight": 3 },
    ...
  },
  "chooseparameters":{
  "roomcategory": { "dict":{
      "Deluxe Double Room": 5,
      "Economy Shared Room": 0,
      ...
      }, "crucial": true, "weight": 5
    },
    "mealtype": { "dict":{
        "breakfast": 3,
        "only_stay": 0,
        ...
        }, "crucial": false, "weight": 2
    }
  },
  "amenities": {
    "swimming_pool": { "crucial": true, "weight": 5 },
    "airport_shuttle": { "crucial": false, "weight": 2 },
    ...
  }
}

"""
)


DEFAULT_WEIGHTS = {
    "pricepernight": 0.7,
    "rating": 0.8,
    "ratingscount": 0.6,
    "starcategory": 0.7,
    "distancetocity": 0.6,
    "distancetounderground": 0.7,
    "distancetobeach": 0.5,
    "distancetoairport": 0.5,
    "popular_location_rank": 0.8,
}


# Normalize numeric field value (example: higher rating is better, lower distance is better)
def normalize_value(field, value):
    # You can refine this per field
    if field in ["rating"]:
        return min(value / 5, 1.0)  # rating out of 10
    elif field in ["starcategory"]:
        return min(value / 5, 1.0)  # star rating out of 5
    elif field in ["ratingscount"]:
        return min(value / 5000, 1.0)  # scale by max 5k reviews
    elif field.startswith("distance") or field == "popular_location_rank":
        return 1 / (1 + value)  # smaller distance/popularity rank = higher score
    elif field == "pricepernight":
        return 1 / (1 + value)  # cheaper = better score
    return 0.0  # fallback


def filter_and_rank_hotels(df, user_preferences):
    df_filtered = pd.DataFrame(df).copy()
    # print(df_filtered.head())
    # 1. Filter by crucial fields
    field_map = {
        "max_price_usd": "pricepernight",
        "min_rating": "rating",
        "min_ratingscount": "ratingscount",
        "min_starcategory": "starcategory",
        "max_starcategory": "starcategory",
        "max_distancetocity": "distancetocity",
        "max_distancetounderground": "distancetounderground",
        "max_distancetobeach": "distancetobeach",
        "max_distancetoairport": "distancetoairport",
        "max_popular_location_rank": "popular_location_rank",
    }
    print(len(df_filtered))
    for key, config in user_preferences.get("fields", {}).items():
        if config["crucial"] and config["value"] is not None and key in field_map:
            col = field_map[key]
            val = config["value"]
            # print(key, col, val)
            # print(df_filtered[col] <= val)
            if key.startswith("max_"):
                df_filtered = df_filtered[df_filtered[col] <= val]
            elif key.startswith("min_"):
                df_filtered = df_filtered[df_filtered[col] >= val]
            else:
                df_filtered = df_filtered[df_filtered[col] == val]
    print("after crutial fields ", len(df_filtered))

    # 2. Filter by crucial amenities
    for amenity, config in user_preferences.get("amenities", {}).items():
        # print(amenity, config)
        # print(df_filtered[amenity])
        if config["crucial"]:
            df_filtered = df_filtered[df_filtered[amenity] == 1]
    print("after crutial amenities ", len(df_filtered))

    # # 3. Filter by crucial chooseparameters
    # for param, config in user_preferences.get("chooseparameters", {}).items():
    #     if config["crucial"]:
    #         chosen_options = config["dict"]
    #         for option, w in chosen_options.items():
    #             if param in df_filtered.columns:
    #                 df_filtered = df_filtered[df_filtered[param] == option]
    # print(len(df_filtered))

    # 4. Scoring phase (non-crucial weighted parameters)
    scores = []
    mentioned_amenities = list(user_preferences.get("amenities", {}).keys())
    mentioned_fields = list(user_preferences.get("fields", {}).keys())
    for idx, row in df_filtered.iterrows():
        score = 0
        max_score = 0

        # Fields
        for field, config in user_preferences.get("fields", {}).items():
            if not config["crucial"] and config["value"] is not None:
                weight = config["weight"]
                max_score += weight
                if field in row:
                    if "max" in field and row[field] <= config["value"]:
                        score += weight
                    elif "min" in field and row[field] >= config["value"]:
                        score += weight

        # scoring non-mentioned fields
        total_score = 0.0
        for field, weight in DEFAULT_WEIGHTS.items():
            if field not in mentioned_fields:
                raw_value = row[field]
            if raw_value is not None:
                normalized = normalize_value(field, raw_value)
                total_score += weight * normalized * 0.3

        for amenity in amenities:
            if (
                amenity not in mentioned_amenities
                and amenity in row
                and row[amenity] == True
            ):
                weight = 0.3
                max_score += weight

        # Amenities
        for amenity, config in user_preferences.get("amenities", {}).items():
            if not config["crucial"]:
                weight = config["weight"]
                max_score += weight
                if amenity in row and row[amenity] == True:
                    score += weight

        # non-mentioned amenities
        for amenity in amenities:
            if (
                amenity not in mentioned_amenities
                and amenity in row
                and row[amenity] == True
            ):
                weight = 0.3
                max_score += weight

        # Chooseparameters (e.g., mealtype, roomcategory)
        for param, config in user_preferences.get("chooseparameters", {}).items():
            # if not config["crucial"]:
            for option, weight in config["dict"].items():
                max_score += weight
                if param in row and row[param] == option:
                    score += weight

        normalized_score = score / max_score if max_score > 0 else 0
        scores.append(normalized_score)

    df_filtered["match_score"] = scores

    return df_filtered.sort_values(by="match_score", ascending=False).reset_index(
        drop=True
    )


def find_matching_hotels(query: str, hotels: dict[str, dict[str, object]]):
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
    # print(SYSTEM_PROMPT)
    # USER_PROMPT = ""  "I'd love to find afordable a family-friendly hotel surrounded by nature, perfect for a peaceful getaway, that also allows an extra bed for children."""
    # USER_PROMPT = """I want to live in a hotel with parking and I have a dog."""
    # USER_PROMPT = """Looking for hotel near the beach with a swimming pool and all included.
    # Prefer something with good reviews and not too far from the city center."""
    print(query, "#########################")
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=SYSTEM_PROMPT,
        input=query,
        temperature=0,
    )
    print(response.output_text)
    match = re.search(r"\{.*\}", response.output_text, re.DOTALL)
    if match:
        json_str = match.group(0)
        user_preferences = json.loads(json_str)
    else:
        print("Error: wrong JSON found in response.")
        return {"fields": {}, "chooseparameters": {}, "amenities": {}}, []
    # user_preferences = json.loads(response.output_text)
    print(user_preferences)
    return user_preferences, filter_and_rank_hotels(hotels, user_preferences)


# wifi, air_conditioning_in_all_rooms, private_bathroom, breakfast, free_onsite_parking, airport_shuttle, swimming_pool, fitness_facilities, restaurant, room_service, twenty_four_hour_reception, accessible, pets_allowed, family_rooms_available, non_smoking_rooms, laundry_service, luggage_storage, flat_screen_tv, concierge_service, multilingual_staff

# print(response.output_text)
