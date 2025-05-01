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


def save_to_csv(hotel_data, output_dir="data/csv"):
    """Save hotel data to CSV files"""
    os.makedirs(output_dir, exist_ok=True)
    for location, df in hotel_data.items():
        file_path = os.path.join(output_dir, f"{location}_hotels.csv")
        df.to_csv(file_path, index=False)
        print(f"Saved {location} data to {file_path}")


def save_to_excel(hotel_data, output_file="data/hotels_data.xlsx"):
    """Save hotel data to Excel file with multiple sheets"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with pd.ExcelWriter(output_file) as writer:
        for location, df in hotel_data.items():
            df.to_excel(writer, sheet_name=location, index=False)
    print(f"Saved all data to {output_file}")


if __name__ == "__main__":
    hotel_data = read_hotel_data()

    # Save data to CSV files
    save_to_csv(hotel_data)

    # Save data to Excel file
    save_to_excel(hotel_data)
