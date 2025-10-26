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
    
def find_topic_by_id(id: str):
    # Search for a topic by id in the 'topics' table in Supabase.
    response = SUPABASE_CLIENT.table("topics").select("id", "*").eq("id", id).execute()
    if response.data:
        return True, response.data[0] # type: ignore
    else:
        return False, None
    
def find_exercise_by_id(id: str):
    # Search for a topic by id in the 'topics' table in Supabase.
    response = SUPABASE_CLIENT.table("exercise").select("id", "*").eq("id", id).execute()
    if response.data:
        return True, response.data[0] # type: ignore
    else:
        return False, None
    
def update_topic(id: str, column: str, value):
    # Update a topic in the 'topics' table in Supabase.
    response = SUPABASE_CLIENT.table("topics").update({column: value}).eq("id", id).execute()
    return response

def decrement_internal_relevance_scores():
    # Decrease all internal relevance scores by 1 using a Supabase RPC function.
    response = SUPABASE_CLIENT.rpc("decrement_scores").execute()
    return response

def get_sorted_topics(limit: int, offset: int):
    # Get topics sorted by relevance score in descending order with pagination.
    response = SUPABASE_CLIENT.table("topics").select("name", "internal_relevance_score", "relevance_score", "date_added").order("relevance_score", desc=True).order("relevance_score", desc=True).order("date_added", desc=True).limit(limit).offset(offset).execute()
    return response.data

# Supabase Authentication Functions

def sign_up(email: str, password: str):
    auth_response = SUPABASE_CLIENT.auth.sign_up({
        "email": email,
        "password": password
    })
    return auth_response

def sign_in(email: str, password: str):
    auth_response = SUPABASE_CLIENT.auth.sign_in({
        "email": email,
        "password": password
    })
    return auth_response

def sign_out():
    auth_response = SUPABASE_CLIENT.auth.sign_out()
    return auth_response

def get_current_user():
    user = SUPABASE_CLIENT.auth.get_user()
    return user

print(get_all_topics_from_supabase())