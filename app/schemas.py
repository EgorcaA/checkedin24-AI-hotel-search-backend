from typing import Any, Dict, List

from pydantic import BaseModel


class Hotel(BaseModel):
    # Include all fields from main_params
    hotel_name: str
    clusterchain: str
    clusterbrand: str
    clustersubbrand: str
    pricepernight: float
    rating: float
    ratingscount: int
    starcategory: int
    mealtype: str
    distancetocity: float
    distancetounderground: float
    distancetobeach: float
    distancetoairport: float
    roomcategory: str
    locationtype: str
    locationname: str
    popular_location_rank: int
    amenities: List[str]


class HotelResponse(BaseModel):
    hotels: List[Hotel]
    user_preferences: Dict[str, Any]
