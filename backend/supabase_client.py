
from supabase import create_client, Client
import os
from dotenv import load_dotenv
#from topic import serialize_for_supabase
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def serialize_for_supabase(data: dict) -> dict:
    """Convert datetime objects to ISO strings or timestamps for Supabase."""
    serialized = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            # Option 1: store ISO string
            serialized[key] = value.isoformat()

            # OR Option 2 (preferred for numeric sorting): store as UNIX timestamp
            # serialized[key] = value.timestamp()
        elif isinstance(value, list):
            # Recursively handle nested lists
            serialized[key] = [
                v.isoformat() if isinstance(v, datetime) else v for v in value
            ]
        else:
            serialized[key] = value
    return serialized

# Inserts a topic into the Supabase 'topics' table.
def insert(table: str, topic_data: dict):
    topic_data = serialize_for_supabase(topic_data)
    response = supabase.table(table).upsert(topic_data, on_conflict="id").execute()
    return response

# Retrieves all topics from the Supabase 'topics' table.
def get_all_topics_from_supabase():
    response = supabase.table('topics').select('*').execute()
    return response.data

def get_info_about_topic(id: str, *columns):
    #
    # Fetch specified columns from the 'topics' table in Supabase.

    # Args:
    #     *columns: Variable number of column names as strings. (e.g. 'name', 'url')

    # Returns:
    #     List of dictionaries with requested column values.
    # 
    if not columns:
        # If no columns are provided, fetch all
        select_str = "*"
    else:
        # Join column names with commas for Supabase select
        select_str = ",".join(columns)

    response = supabase.table('topics').select("id", select_str).execute()


    return response.data
