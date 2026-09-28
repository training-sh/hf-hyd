"""Edit these settings when your temporary sandbox changes. No secrets here."""
import os

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gcp-ai-sandb-403-96741179")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
EMBEDDING_LOCATION = os.getenv("EMBEDDING_LOCATION", "us-central1")
MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

def make_client(location=None):
    from google import genai
    from google.genai import types
    return genai.Client(vertexai=True, project=PROJECT_ID,
                        location=location or LOCATION,
                        http_options=types.HttpOptions(api_version="v1"))
