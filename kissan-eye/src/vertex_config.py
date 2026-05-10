import os
import vertexai
from dotenv import load_dotenv

load_dotenv()

def init_vertex():
    project  = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_LOCATION")

    if not project:
        raise ValueError("GCP_PROJECT_ID missing from .env")

    vertexai.init(project=project, location=location)
    print(f"[OK] Vertex AI initialized -- project: {project}, location: {location}")
