from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inserts a topic into the Supabase 'topics' table.
def insert_topic(topic_data: dict):
    response = supabase.table('topics').upsert(topic_data, on_conflict="date_created").execute()
    return response

# Retrieves all topics from the Supabase 'topics' table.
def get_all_topics():
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
