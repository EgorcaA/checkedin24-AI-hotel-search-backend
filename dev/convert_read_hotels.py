import os

import numpy as np
import pandas as pd


def read_hotel_data():
    # Read hotel data from Parquet files
    data_dir = "data/hotels"
    hotel_files = {
        "Copenhagen": "resultlist_Kopenhagen.parquet",
        "Mallorca": "resultlist_Mallorca.parquet",
        "New York": "resultlist_New York.parquet",
    }

    # Read and store data for each location
    hotel_data = {}
    for location, filename in hotel_files.items():
        file_path = os.path.join(data_dir, filename)
        hotel_data[location] = pd.read_parquet(file_path)
        print(f"\n{location} Hotels Data:")
        print(f"Number of hotels: {len(hotel_data[location])}")
        print("\nFirst few rows:")
        print(hotel_data[location].head())
        print("\nColumns:")
        print(hotel_data[location].columns.tolist())

    return hotel_data


if __name__ == "__main__":
    hotel_data = read_hotel_data()
