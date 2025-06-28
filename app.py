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

# Get the collection
movie_collection = client.collections.get("Movie")

# Fetch up to 10 movies (default is 10)
results = movie_collection.query.fetch_objects(
    limit=10,
    return_properties=["title", "plot", "genres", "year"]
)

print("data:  ",len(results.objects))
# Display results
for obj in results.objects:
    props = obj.properties
    print(f"Title: {props['title']}")
    print(f"Genres: {props['genres']}")
    print(f"Year: {props['year']}")
    print(f"Plot: {props['plot']}\n---")


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
