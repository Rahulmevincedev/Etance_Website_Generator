import os
import json
from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import LangSmithAuthError
import requests
from uuid import UUID
from datetime import datetime
from decimal import Decimal

def json_serializer(obj):
    """Custom JSON serializer to handle UUID, datetime, and Decimal objects."""
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def export_langsmith_run():
    """
    Connects to Langsmith, fetches a run by ID, and saves its data to a file
    in a 'logs' directory, named after the run ID.
    """
    load_dotenv()
    print("Attempting to load environment variables from .env file...")

    try:
        client = Client()
        run_id_to_export = os.getenv("RUN_ID_TO_EXPORT")
        if not run_id_to_export:
            print("❌ Error: The 'RUN_ID_TO_EXPORT' variable is not set in your .env file.")
            return

        print(f"Fetching data for run ID: {run_id_to_export}...")
        run = client.read_run(run_id=run_id_to_export)
        run_data = run.dict()

        # --- New File Saving Logic ---
        
        # 1. Define the logs directory and create it if it doesn't exist.
        log_directory = "logs"
        os.makedirs(log_directory, exist_ok=True)

        # 2. Construct the full file path using the run ID as the name.
        file_path = os.path.join(log_directory, f"{run_id_to_export}.json")
        
        # 3. Write the JSON data to the file.
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(run_data, f, indent=2, default=json_serializer)
        
        # 4. Print a confirmation message.
        print(f"\n✅ Successfully fetched and saved run data to: {file_path}")

    except LangSmithAuthError:
        print("\n❌ Authentication Error: Failed to authenticate with Langsmith.")
        print("Please double-check that your LANGSMITH_API_KEY is correct.")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: Failed to fetch the run. Status: {e.response.status_code}")
        print(f"   Response from server: {e.response.text}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    export_langsmith_run()