""" Make interacting with database a lot easier through helper functions """

# Dependencies
from dotenv import load_dotenv
from general import SUPABASE_CLIENT

load_dotenv()

def add_topic_visited(user_id: str, topic_id: str):
    #Fetching topic_visited
    response = SUPABASE_CLIENT.table("sensitive_info").select("id", "topics_visited").eq("id", user_id).execute()
    topics_visited = response.data[0]["topics_visited"]
    topics_visited.append(topic_id)
    response = SUPABASE_CLIENT.table("sensitive_info").update({"topics_visited": topics_visited}).eq("id", user_id).execute()
    return response

def add_completed_exercise(user_id: str, exercise_id: str):
    #Fetching completed_exercises
    response = SUPABASE_CLIENT.table("sensitive_info").select("id", "completed_exercises").eq("id", user_id).execute()
    completed_exercises = response.data[0]["completed_exercises"]
    completed_exercises.append(exercise_id)
    response = SUPABASE_CLIENT.table("sensitive_info").update({"completed_exercises": completed_exercises}).eq("id", user_id).execute()
    return response

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

def decrement_internal_relevance_scores():
    # Decrease all internal relevance scores by 1 using a Supabase RPC function.
    response = SUPABASE_CLIENT.rpc("decrement_scores").execute()
    return response

def get_sorted_topics(limit: int, offset: int):
    # Get topics sorted by relevance score in descending order with pagination.
    response = SUPABASE_CLIENT.table("topics").select("id", "name", "internal_relevance_score", "relevance_score", "date_added").order("internal_relevance_score", desc=True).order("relevance_score", desc=True).order("date_added", desc=True).limit(limit).offset(offset).execute()
    return response.data


# Supabase Authentication Functions
# These functions should be be assigned to a user.

def sign_up(email: str, password: str):
    auth_response = SUPABASE_CLIENT.auth.sign_up({
        "email": email,
        "password": password
    })

    SUPABASE_CLIENT.table("sensitive_info").insert({
        "id": auth_response.user.id,
        "date_joined": auth_response.user.created_at.isoformat(),
        "topics_visited": [],
        "completed_exercises": []
    }).execute()
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

#sign_up("useruserues@example.com", "password12ttttttttt3")
add_topic_visited("2574ac1a-be84-48e7-ad02-3eaffcd71366", "dbcd3fb8-7e9c-46d4-8a49-2c8ec96922f3")




