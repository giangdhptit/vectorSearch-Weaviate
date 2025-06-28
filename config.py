# config.py
import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    # Weaviate Configuration
    WEAVIATE_URL = "https://svgmipczrciw1mctcybq.c0.europe-west3.gcp.weaviate.cloud"
    WEAVIATE_API_KEY = "dGRWU2ZHR0RSSXFqR0F2dV9EdjQxYlptWFlRY0xxV2Nuc0w2ak0xWVJxTDlUSUw2UGYxQUFZeG1HUjRzPV92MjAw"
    
    # Embeddings Model
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"