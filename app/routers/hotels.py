import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..logger import get_logger
from ..params import amenities, main_params

# from ..sample_data import hotels
# from ..get_results import find_matching_hotels
from ..process_hotels import find_matching_hotels
from ..schemas import HotelResponse

logger = get_logger(__name__)

router = APIRouter()
# print(os.path.abspath('.'))


# Get data path from environment variable or use default
DATA_DIR = os.getenv("HOTEL_DATA_DIR", "/app/data")
DATA_PATH = Path(DATA_DIR) / "csv" / "Copenhagen_hotels_clean.csv"

logger.info(f"Attempting to load hotel data from {DATA_PATH}")

try:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Hotel data file not found at {DATA_PATH}")

    pd.set_option("display.max_columns", None)
    hotels_1 = pd.read_csv(DATA_PATH)
    ddhotels = hotels_1.to_dict(orient="records")
    logger.info(f"Successfully loaded {len(ddhotels)} hotels")
except Exception as e:
    logger.error(f"Failed to load hotel data: {str(e)}")
    raise HTTPException(status_code=500, detail=f"Failed to load hotel data: {str(e)}")


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
    logger.debug("Transforming hotels data")
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
    logger.debug(f"Transformed {len(hotels_result)} hotels")
    return hotels_result


@router.get("/hotels", response_model=HotelResponse)
async def get_hotels(
    prompt: str = Query(None, description="Filter hotels by name or location")
):
    logger.info(f"Received request for hotels with prompt: {prompt}")

    if not prompt:
        logger.debug("No prompt provided, returning all hotels")
        return HotelResponse(
            hotels=transform_hotels(hotels_1)[:10], user_preferences={}
        )

    prompt = prompt.lower()
    logger.debug(f"Processing prompt: {prompt}")

    user_preferences, matching_hotels = find_matching_hotels(
        prompt, ddhotels
    )  # Dict[str, Any], pd.Dataframe
    if len(matching_hotels) == 0:
        logger.warning(f"No hotels found matching prompt: {prompt}")
        return HotelResponse(hotels=[], user_preferences=user_preferences)

    hotel_names = matching_hotels["hotel_name"].tolist()
    logger.info(
        f"Found {len(matching_hotels)} hotels matching the prompt, {hotel_names}"
    )
    return HotelResponse(
        hotels=transform_hotels(matching_hotels), user_preferences=user_preferences
    )
