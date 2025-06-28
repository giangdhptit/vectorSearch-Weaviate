# connect.py
import os
import weaviate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

if not weaviate_url or not weaviate_api_key:
    print("Error: Missing Weaviate configuration in .env file")
    exit(1)

# Initialize client
try:
    client = weaviate.Client(
        url=weaviate_url,
        auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key)
    )
    
    # Test connection
    meta = client.get_meta()
    print("✅ Successfully connected to Weaviate!")
    print(f"Version: {meta['version']}")
    print(f"Modules: {', '.join(module['name'] for module in meta['modules'])}")
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
    print("Please verify:")
    print("1. Your Weaviate cluster URL is correct")
    print("2. Your API key is valid")
    print("3. Your internet connection is working")
    print("4. The Weaviate service is running")