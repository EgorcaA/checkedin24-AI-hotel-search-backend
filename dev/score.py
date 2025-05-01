import json
import os
import re

import dotenv
import numpy as np
import openai
import pandas as pd
from openai import AzureOpenAI
from params import amenities, amenities_german, gptparams
from prompts import system_prompt
from sentence_transformers import SentenceTransformer, util


def read_hotel_data():
    # Read hotel data from Parquet files
    data_dir = "data/hotels"
    hotel_files = {
        "Copenhagen": "resultlist_Kopenhagen.parquet",
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
        # print("\nColumns:")
        # print(hotel_data[location].columns.tolist())

    return hotel_data


def add_amenities_score(df, amenities_params):
    score = np.zeros(len(df))
    for param in amenities_params:
        field = param["field"]
        value = param["value"]
        # Score is 1 if value matches, 0 if NaN or doesn't match
        match = (df[field] == value) & (~df[field].isna())
        score += match.astype(int) * param["importance"]
    df["amenities_score"] = score
    return df


def add_main_features_score(df, main_params):
    """
    Add a score based on main parameters with the following rules:
    - For numeric comparisons (price, rating, stars): strict 0 if not satisfied, growing score if satisfied
    - For categorical values (popularity, mealtype, etc.): exact match required
    - For boolean values: exact match required
    - NaN values always get 0 score
    """
    score = np.zeros(len(df))

    for param in main_params:
        field = param["field"]
        value = param["value"]
        importance = param["importance"]

        if field not in df.columns:
            continue

        # Handle numeric comparisons
        if field in ["pricepernight", "rating", "starcategory"]:
            if "less than" in str(value):
                threshold = float(value.split("less than")[1].strip())
                match = (df[field] < threshold) & (~df[field].isna())
                score += match.astype(float) * importance
            elif "greater than" in str(value):
                threshold = float(value.split("greater than")[1].strip())
                match = (df[field] > threshold) & (~df[field].isna())
                score += match.astype(float) * importance
            elif "at least" in str(value):
                threshold = float(value.split("at least")[1].strip().split("/")[0])
                match = (df[field] >= threshold) & (~df[field].isna())
                score += match.astype(float) * importance
            else:
                # Exact match for other numeric values
                match = (df[field] == value) & (~df[field].isna())
                score += match.astype(float) * importance

        # Handle categorical values
        elif field in ["popularity", "mealtype", "locationtype"]:
            match = (df[field] == value) & (~df[field].isna())
            score += match.astype(float) * importance

        # Handle boolean values
        elif field in ["cancelable"]:
            match = (df[field] == value) & (~df[field].isna())
            score += match.astype(float) * importance

        # Handle text fields (exact match)
        elif field in [
            "hotel_name",
            "clusterchain",
            "clusterbrand",
            "roomcategory",
            "locationname",
        ]:
            match = (df[field] == value) & (~df[field].isna())
            score += match.astype(float) * importance

        # Handle numeric fields with exact match
        elif field in ["numrooms", "numadults", "numchildren"]:
            match = (df[field] == value) & (~df[field].isna())
            score += match.astype(float) * importance

    df["main_features_score"] = score
    return df


def count_words(prompt):
    words = prompt.split()
    return len(words)


def generate_gpt_prompt(top_20_hotels, user_prompt):
    """
    Generate a prompt for GPT to analyze and sort the top 20 hotels based on their scores and features.
    """
    prompt = f"""Analyze and sort these top 20 hotels based on their relevance to user prompt.
    Consider both the main parameters and amenities in your analysis.

    Prompt:
    {user_prompt}

    Hotel Data:
    {top_20_hotels.to_string()}

    Please provide a JSON response with the following structure:
    {{
        "hotels": [
            {{
                "searchid": "hotel_id",
                "rank": 1,
                "explanation": "Why this hotel is a good choice",
                "strengths": ["strength1", "strength2"],
                "drawbacks": ["drawback1", "drawback2"]
            }},
            ...
        ],
        "summary": "Brief summary of what makes these hotels stand out",
        "patterns": ["pattern1", "pattern2"]
    }}

    Focus on:
    - How well they match the main parameters (rating and price requirements)
    - The variety and quality of amenities they offer
    - The balance between price and quality
    - Any unique features that make them particularly attractive
    """
    return prompt


if __name__ == "__main__":

    # user_prompt =    "Find me a hotel with rating at least 9.3 and cheaper than 40 EUR per night."
    # user_prompt = "I'm looking for a hotel with a breathtaking view and a luxurious wellness center where I can truly relax."
    # user_prompt = "I'm travelling with a dog and need a parking space."
    # user_prompt =    "I'm looking for a hotel with a breathtaking view and a luxurious wellness center where I can truly relax."
    # user_prompt =    "I'd love to find a family-friendly hotel surrounded by nature, perfect for a peaceful getaway, that also allows an extra bed for children."
    user_prompt = "Stylish, modern hotel that not only offers great design but also serves an good breakfast."
    print(user_prompt)
    # user_prompt =    "Find me a hotel with rating at least 9.3 and cheaper than 40 EUR per night."

    vecmodel = SentenceTransformer("all-MiniLM-L6-v2")
    tag_embeddings = vecmodel.encode(amenities, normalize_embeddings=True)
    user_embedding = vecmodel.encode(user_prompt, normalize_embeddings=True)
    # Compute similarity
    cos_scores = np.dot(tag_embeddings, user_embedding)

    # Get top matching tags
    top_indices = np.argsort(cos_scores)[::-1][:20]
    top_scores = [cos_scores[i] for i in top_indices]
    indices_high = top_indices[np.array(top_scores) > 0.4]
    top_tags = [amenities[i] for i in indices_high]
    top_tags_ge = [amenities_german[i] for i in indices_high]
    toptop_scores = [cos_scores[i] for i in indices_high]

    amenities_factor = 0.7
    amenities_params = []
    for i in range(len(top_tags)):
        amenities_params.append(
            {
                "field": top_tags_ge[i],
                "value": True,
                "importance": float(amenities_factor * toptop_scores[i]),
            }
        )

    # Print amenities parameters in a nice column format
    print("\nAmenities Parameters:")
    print("-" * 80)
    print(f"{'Amenity':<50} {'Importance':<10}")
    print("-" * 80)
    for param in amenities_params:
        print(f"{param['field']:<50} {param['importance']:.4f}")
    print("-" * 80)
    print()

    dotenv.load_dotenv(".env")
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    client = AzureOpenAI(
        api_key=openai.api_key,
        api_version="2025-01-01-preview",
        azure_endpoint=openai.azure_endpoint,
    )
    deployment_name = "gpt-4o-0806-eu"

    response = client.chat.completions.create(
        model=deployment_name,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    parsed_data = response.choices[0].message.content
    main_params = json.loads(parsed_data)
    # print(main_params)
    # Print amenities parameters in a nice column format
    print("\nMain Parameters:")
    print("-" * 80)
    print(f"{'Parameter':<50} {'Importance':<10}")
    print("-" * 80)
    for param in main_params:
        print(f"{param['field']:<50} {param['importance']:.4f}")
    print("-" * 80)
    print()
    # main_params = [
    #     {"field": "rating", "value": "at least 9.3/10", "importance": 0.9},
    # {"field": "pricepernight", "value": "less than 40", "importance": 1.0}
    # ]

    # amenities_params = [{'field': 'amenity_Hotel', 'value': True, 'importance': 0.4037533104419708},
    # {'field': 'amenity_Luxushotel',
    # 'value': True,
    # 'importance': 0.39246296882629395},
    # {'field': 'amenity_Businesshotel',
    # 'value': True,
    # 'importance': 0.3807050585746765},
    # {'field': 'amenity_Boutique-/Designhotel',
    # 'value': True,
    # 'importance': 0.34293198585510254},
    # {'field': 'amenity_Strandhotel',
    # 'value': True,
    # 'importance': 0.322694331407547},
    # {'field': 'amenity_Wellnesshotel',
    # 'value': True,
    # 'importance': 0.31551241874694824},
    # {'field': 'amenity_Haustierfreundliches Hotel',
    # 'value': True,
    # 'importance': 0.3010227382183075},
    # {'field': 'amenity_Resort', 'value': True, 'importance': 0.2920161783695221},
    # {'field': 'amenity_Pension',
    # 'value': True,
    # 'importance': 0.28953832387924194}]

    hotel_data = read_hotel_data()

    # Add scores to each DataFrame
    for location, df in hotel_data.items():
        hotel_data[location] = add_amenities_score(df, amenities_params)
        hotel_data[location] = add_main_features_score(df, main_params)
        # Add total score
        hotel_data[location]["total_score"] = (
            hotel_data[location]["amenities_score"]
            + hotel_data[location]["main_features_score"]
        )

        # Get top 20 hotels
        top_20 = (
            hotel_data[location].sort_values("total_score", ascending=False).head(20)
        )

        print(f"\nTop 20 Hotels in {location} (ranked by total score):")
        print("=" * 100)
        print(
            top_20[
                [
                    "hotel_name",
                    "rating",
                    "pricepernight",
                    "amenities_score",
                    "main_features_score",
                    "total_score",
                ]
            ].to_string()
        )
        print("=" * 100)

        # Generate GPT prompt
        gpt_prompt = generate_gpt_prompt(top_20[gptparams], user_prompt)

        print("\nGPT Analysis Prompt:")
        print("=" * 100)
        # print(gpt_prompt)
        print("=" * 100)
        print(count_words(gpt_prompt))
        break

    response = client.chat.completions.create(
        model=deployment_name,
        temperature=0,
        messages=[{"role": "user", "content": gpt_prompt}],
    )

    try:
        # Parse the JSON response
        # print(response.choices[0].message.content)

        raw = response.choices[0].message.content
        # Try to extract the first {...} block
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            json_str = match.group(0)
            gpt_response = json.loads(json_str)
        else:
            print("No JSON found in response.")
        # gpt_response = json.loads(response.choices[0].message.content)

        # Process each hotel in the response
        for hotel in gpt_response["hotels"]:
            # Find the hotel in the database using searchid
            hotel_data = top_20[top_20["searchid"] == hotel["searchid"]].iloc[0]

            # Add non-amenity fields
            for column in hotel_data.index:
                if not column.startswith("amenity_"):
                    hotel[column] = hotel_data[column]

            # Add list of true amenities
            hotel["amenities"] = [
                col.replace("amenity_", "")
                for col in hotel_data.index
                if col.startswith("amenity_") and hotel_data[col] == True
            ]

        # Print the enriched response
        print("\nEnriched GPT Analysis:")
        print("=" * 100)
        print(json.dumps(gpt_response, indent=2, ensure_ascii=False))
        print("=" * 100)

    except json.JSONDecodeError as e:
        print("Error parsing GPT response as JSON:")
        print(response.choices[0].message.content)
        print(f"Error details: {str(e)}")
    except Exception as e:
        print(f"Error processing GPT response: {str(e)}")
        print("Original response:")
        print(response.choices[0].message.content)
