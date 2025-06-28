import streamlit as st
import weaviate
from sentence_transformers import SentenceTransformer
from config import Config
import logging

import os
import weaviate
from sentence_transformers import SentenceTransformer
from config import Config
from tqdm import tqdm
import json
from tqdm import tqdm
from weaviate import Client
from weaviate.classes.query import Filter
from weaviate.collections import Collection
import weaviate.classes as wvc

# Path to your JSON file
file_path = 'sample_mflix.movies.json'

# Read the JSON file
with open(file_path, 'r') as json_file:
    movies_data = json.load(json_file)

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

# Initialize the Weaviate client
weaviate_client = weaviate.connect_to_weaviate_cloud(
        cluster_url=Config.WEAVIATE_URL,
        auth_credentials=weaviate.auth.AuthApiKey(Config.WEAVIATE_API_KEY),
        skip_init_checks=True  # Prevent gRPC timeout issues
    )

# Retrieve meta information to check version
try:
    meta_data = weaviate_client.query.get("Meta").with_additional(["version"]).do()
    version = meta_data.get('version', 'Unknown version')
    print(f"Connected to Weaviate version: {version}")
except Exception as e:
    print(f"Failed to retrieve Weaviate version: {e}")

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define Weaviate schema
# class_obj = {
#     "class": "Movie",
#     "vectorizer": "none",
#     "properties": [
#         {"name": "title", "dataType": ["text"]},
#         {"name": "plot", "dataType": ["text"]},
#         {"name": "genres", "dataType": ["text[]"]},
#         {"name": "year", "dataType": ["int"]}
#     ]
# }

class_obj={
  "class": "Movie",
  "description": "A movie object imported from JSON dataset",
  "vectorizer": "none",
  "properties": [
    { "name": "title", "dataType": ["text"] },
    { "name": "plot", "dataType": ["text"] },
    { "name": "fullplot", "dataType": ["text"] },
    { "name": "genres", "dataType": ["text[]"] },
    { "name": "cast", "dataType": ["text[]"] },
    { "name": "directors", "dataType": ["text[]"] },
    { "name": "writers", "dataType": ["text[]"] },
    { "name": "languages", "dataType": ["text[]"] },
    { "name": "countries", "dataType": ["text[]"] },
    { "name": "poster", "dataType": ["text"] },
    { "name": "rated", "dataType": ["text"] },
    { "name": "type", "dataType": ["text"] },
    { "name": "released", "dataType": ["date"] },
    { "name": "dvd", "dataType": ["date"] },
    { "name": "lastupdated", "dataType": ["text"] },

    { "name": "runtime", "dataType": ["number"] },
    { "name": "year", "dataType": ["number"] },

    { "name": "imdb_rating", "dataType": ["number"] },
    { "name": "imdb_votes", "dataType": ["number"] },
    { "name": "imdb_id", "dataType": ["number"] },

    { "name": "awards_wins", "dataType": ["number"] },
    { "name": "awards_nominations", "dataType": ["number"] },
    { "name": "awards_text", "dataType": ["text"] },

    { "name": "tomato_viewer_rating", "dataType": ["number"] },
    { "name": "tomato_viewer_numReviews", "dataType": ["number"] },
    { "name": "tomato_viewer_meter", "dataType": ["number"] },
    
    { "name": "tomato_critic_rating", "dataType": ["number"] },
    { "name": "tomato_critic_numReviews", "dataType": ["number"] },
    { "name": "tomato_critic_meter", "dataType": ["number"] },

    { "name": "tomato_fresh", "dataType": ["number"] },
    { "name": "tomato_rotten", "dataType": ["number"] },

    { "name": "tomato_lastUpdated", "dataType": ["date"] },
    { "name": "num_mflix_comments", "dataType": ["number"] }
  ]
}


# if not weaviate_client.collections.get("Movie"):
# weaviate_client.collections.create("Movie")
weaviate_client.collections.delete("Movie")  # THIS WILL DELETE THE SPECIFIED COLLECTION(S) AND THEIR OBJECTS
weaviate_client.collections.create_from_dict(class_obj)


# Import data
batch_size = 50
movies = movies_data[:4000]

# Adjust limit as needed
print(movies)

movies_weaviate = weaviate_client.collections.get("Movie")

for movie in tqdm(movies, desc="Importing to Weaviate"):
    try:
        # Construct the text for embedding
        text = f"{movie['title']}: {movie.get('plot', '')}"
        
        # Generate the embedding for the text
        embedding = model.encode(text).tolist()
        
        # Create the movie data object in Weaviate
        movies_weaviate.data.insert(
            properties={
                "title": movie["title"],
                "plot": movie.get("plot", ""),
                "genres": movie.get("genres", []),
                "year": movie.get("year", 0)
            },
            vector=embedding
        )
        
    except Exception as e:
        # Log the error (you can also log it to a file or handle differently)
        print(f"Error importing movie {movie['title']}: {str(e)}")

print("Data import completed!")
weaviate_client.close()