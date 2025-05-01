import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..params import amenities, main_params

# from ..sample_data import hotels
# from ..get_results import find_matching_hotels
from ..process_hotels import find_matching_hotels
from ..schemas import HotelResponse

router = APIRouter()
# print(os.path.abspath('.'))


# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "csv" / "Copenhagen_hotels_clean.csv"

pd.set_option("display.max_columns", None)
hotels_1 = pd.read_csv(DATA_PATH)
# hotels_1 = hotels_1.rename(columns={"hotel_name": "name"})
ddhotels = hotels_1.to_dict(orient="records")


# Add this mapping based on your schema
param_types = {
    "hotel_name": str,
    "clusterchain": str,
    "clusterbrand": str,
    "clustersubbrand": str,
    "pricepernight": float,
    "rating": float,
    "ratingscount": int,
    "starcategory": int,
    "mealtype": str,
    "distancetocity": float,
    "distancetounderground": float,
    "distancetobeach": float,
    "distancetoairport": float,
    "roomcategory": str,
    "locationtype": str,
    "locationname": str,
    "popular_location_rank": int,
}


def transform_hotels(hotels: pd.DataFrame) -> List[Dict[str, Any]]:
    hotels_result = []
    for i, row in hotels.iterrows():
        hotel = {}
        for param in main_params:
            value = row[param]
            if pd.isna(value):
                if param_types.get(param) == str:
                    hotel[param] = ""
                elif param_types.get(param) == int:
                    hotel[param] = 0
                elif param_types.get(param) == float:
                    hotel[param] = 0.0
                else:
                    hotel[param] = None
            else:
                hotel[param] = value
        # Add list of true amenities
        hotel["amenities"] = [col for col in amenities if row[col] == True]
        # print(hotel)
        hotels_result.append(hotel)
    return hotels_result


@router.get("/hotels", response_model=HotelResponse)
async def get_hotels(
    prompt: str = Query(None, description="Filter hotels by name or location")
):
    if not prompt:
        return HotelResponse(hotels=transform_hotels(hotels_1), user_preferences={})

    prompt = prompt.lower()

    print("#########################")
    print(prompt)
    user_preferences, matching_hotels = find_matching_hotels(prompt, ddhotels)
    if len(matching_hotels) == 0:
        return HotelResponse(hotels=[], user_preferences=user_preferences)

    # print(matching_hotels)

    return HotelResponse(
        hotels=transform_hotels(matching_hotels), user_preferences=user_preferences
    )
