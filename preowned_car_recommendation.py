# -*- coding: utf-8 -*-
"""preowned_car_recommendation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17Vpr9eWhV5A-9wF7wooFZxOKnDAh-dd5
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy.sparse import hstack

"""# Load dataset"""

df = pd.read_csv('/content/OLX_cars.csv')
df.head()

"""
# Combine relevant text features for similarity analysis"""

df['combined_features'] = (
    df['Description'].fillna('') + ' ' +
    df['Car Features'].fillna('')
)

"""# TF-IDF vectorization for text features"""

tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_features'])

"""# Standardize numerical features"""

numerical_features = ['Price', 'KM\'s driven']  # Only using necessary numerical features
scaler = StandardScaler()
scaled_numerical = scaler.fit_transform(df[numerical_features])

"""# Dynamically identify one-hot encoded categorical columns"""

fuel_columns = [col for col in df.columns if 'Fuel' in col]
transmission_columns = [col for col in df.columns if 'Transmission' in col]

"""# Combine all features"""

combined_matrix = hstack([tfidf_matrix, scaled_numerical])

"""# Compute cosine similarity matrix"""

cosine_sim = cosine_similarity(combined_matrix, combined_matrix)

"""# Recommendation function"""

def recommend_cars(car_index, top_n=5):
    """
    Recommend cars based on a given car's index.

    Args:
        car_index (int): Index of the car to base recommendations on.
        top_n (int): Number of recommendations to return.

    Returns:
        pd.DataFrame: DataFrame of top N recommended cars.
    """
    similarity_scores = list(enumerate(cosine_sim[car_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    top_indices = [i[0] for i in similarity_scores[1:top_n+1]]  # Exclude the input car itself

    # Columns to display
    recommendation_columns = ['Car Name', 'Price', 'KM\'s driven', 'Condition'] + fuel_columns + transmission_columns
    recommendation_columns = [col for col in recommendation_columns if col in df.columns]  # Ensure columns exist

    return df.iloc[top_indices][recommendation_columns]

"""# User input function"""

def get_user_input():
    """
    Accept user input for car preferences and return a feature vector.
    """
    car_name = input("Enter car name or brand (e.g., Toyota Corolla): ").lower()
    max_price = float(input("Enter your budget (e.g., 2000000): "))
    max_kms = float(input("Enter maximum KM's driven (e.g., 50000): "))
    fuel_type = input("Enter fuel preference (Petrol/Diesel/Electric/Hybrid): ").capitalize()
    transmission_type = input("Enter transmission preference (Manual/Automatic): ").capitalize()

    return car_name, max_price, max_kms, fuel_type, transmission_type

"""# Function to find the best match based on user preferences"""

def find_best_match(car_name, max_price, max_kms, fuel_type, transmission_type):
    """
    Finds the best matching car in the dataset based on user input.
    """
    filtered_df = df[
        (df['Price'] <= max_price) &
        (df['KM\'s driven'] <= max_kms) &
        (df['Car Name'].str.lower().str.contains(car_name)) &
        (df[f'Fuel_{fuel_type}'] == 1 if f'Fuel_{fuel_type}' in df.columns else True) &
        (df[f'Transmission_{transmission_type}'] == 1 if f'Transmission_{transmission_type}' in df.columns else True)
    ]

    if filtered_df.empty:
        print("No exact match found. Recommending based on closest price.")
        filtered_df = df.loc[(df['Price'] - max_price).abs().idxmin()]

    return filtered_df.index[0] if not filtered_df.empty else None

"""# Main program"""

def main():
    print("Welcome to the Car Recommendation System!")

    # Get user input
    user_input = get_user_input()
    car_index = find_best_match(*user_input)

    if car_index is not None:
        print(f"\nBase car for recommendation: {df.iloc[car_index]['Car Name']}")
        recommended_cars = recommend_cars(car_index, top_n=5)
        print("\nRecommended Cars:")
        print(recommended_cars)
    else:
        print("No suitable cars found for your preferences.")

"""# Run the program"""

if __name__ == "__main__":
    main()