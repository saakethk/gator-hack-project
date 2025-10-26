""" Make interacting with database a lot easier through helper functions """

# Dependencies
from dotenv import load_dotenv
from general import SUPABASE_CLIENT

load_dotenv()

def insert(table: str, topic_data: dict):
    # Inserts a topic into the Supabase 'topics' table.
    response = SUPABASE_CLIENT.table(table).upsert(topic_data, on_conflict="id").execute()
    return response

def get_all_topics_from_supabase():
    # Retrieves all topics from the Supabase 'topics' table.
    response = SUPABASE_CLIENT.table('topics').select('*').execute()
    return response.data

def get_info_about_topic(id: str, *columns):
    # Fetch specified columns from the 'topics' table in Supabase.
    if not columns:
        # If no columns are provided, fetch all
        select_str = "*"
    else:
        # Join column names with commas for Supabase select
        select_str = ",".join(columns)
    response = SUPABASE_CLIENT.table('topics').select("id", select_str).eq("id", id).execute()
    return response.data

def find_topic_by_name(name: str):
    # Search for a topic by name in the 'topics' table in Supabase.
    response = SUPABASE_CLIENT.table("topics").select("name", "id").eq("name", name).execute()
    if response.data:
        return True, response.data[0]['id'] # type: ignore
    else:
        return False, None
    
def update_topic(id: str, column: str, value):
    # Update a topic in the 'topics' table in Supabase.
    response = SUPABASE_CLIENT.table("topics").update({column: value}).eq("id", id).execute()
    return response