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
