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
class_obj = {
    "class": "Movie",
    "vectorizer": "none",
    "properties": [
        {"name": "title", "dataType": ["text"]},
        {"name": "plot", "dataType": ["text"]},
        {"name": "genres", "dataType": ["text[]"]},
        {"name": "year", "dataType": ["int"]}
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

movies_weaviate = weaviate_client.collections.get("JeopardyQuestion")

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


#####################################################
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Weaviate and embedding model
try:
    auth = weaviate.auth.AuthApiKey(Config.WEAVIATE_API_KEY)
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=Config.WEAVIATE_URL,
        auth_credentials=weaviate.auth.AuthApiKey(Config.WEAVIATE_API_KEY),
        skip_init_checks=True  # Prevent gRPC timeout issues
    )
    model = SentenceTransformer(Config.EMBEDDING_MODEL)
    logger.info(f"✅ Successfully initialized Weaviate client and model")
except Exception as e:
    st.error(f"❌ Failed to connect to Weaviate or load model.  Error: {str(e)}")
    st.stop()

# Streamlit UI
st.title("🎬 Huong-giang (Emmy) Movie Search with Weaviate 🎬")
st.write("Search for movies using natural language queries.")

query = st.text_input("Enter your search query:", placeholder="e.g. epic science fiction with aliens")

if query:
    try:
        # Get the collection
        movie_collection = client.collections.get("Movie")

        # Generate embedding
        vector = model.encode(query).tolist()

        # Perform semantic search
        results = movie_collection.query.near_vector(
            near_vector=vector,
            limit=5,
            return_properties=["title", "genres", "year"],
            return_metadata=["distance"]
        )

        if not results.objects:
            st.warning("No movies found matching your query.")
        else:
            st.success(f"Found {len(results.objects)} result(s):")
            for obj in results.objects:
                props = obj.properties
                st.subheader(props.get("title", "Untitled"))
                st.write(f"**Score:** {obj.metadata.distance:.4f}")
                st.write(f"**Release Date:** {props.get('release_date', 'N/A')}")
                st.write(f"**Genres:** {', '.join(props.get('genres', []))}")
                st.write(f"**Overview:** {props.get('overview', 'No overview available.')}")
                st.markdown("---")

    except Exception as e:
        logger.error(f"Search error: {e}")
        st.error(f"Search error: {str(e)}")

# Clean up
client.close()
