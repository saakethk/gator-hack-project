""" Gets all relevant api keys and such for api calls """

# Dependencies
from firebase_functions import https_fn, scheduler_fn, options
from firebase_admin import initialize_app
from scraper import get_all_topics
from excercise_generator import generate_mcqs_for_story
from database import insert, get_sorted_topics, find_topic_by_id, find_exercise_by_id, decrement_internal_relevance_scores
from database import sign_up, sign_in, sign_out, get_current_user #supabase auth functions
from chat import chatbot
from recommender import recommender
import json

initialize_app()

@https_fn.on_request(timeout_sec=300, memory=options.MemoryOption.GB_1, cors=options.CorsOptions(
        cors_origins=[r"*"],
        cors_methods=["get"],
    ))
def chat_request(req: https_fn.Request) -> https_fn.Response:
    query = req.args.get('query')
    topic = req.args.get('topic')
    history = req.args.get('history')
    res = chatbot(user_input=query, topic=topic, history=history)
    return https_fn.Response(res)

@https_fn.on_request(timeout_sec=300, memory=options.MemoryOption.GB_1, cors=options.CorsOptions(
        cors_origins=[r"*"],
        cors_methods=["get"],
    ))
def send_email_and_password(req: https_fn.Request) -> https_fn.Response:
    email = req.args.get('email')
    password = req.args.get('password')
    res = sign_up(email, password) # call backend function
    return https_fn.Response(res)

@https_fn.on_request(timeout_sec=300, memory=options.MemoryOption.GB_1, cors=options.CorsOptions(
        cors_origins=[r"*"],
        cors_methods=["get"],
    ))
def fetch_supabase_topics(req: https_fn.Request) -> https_fn.Response:
    offset = int(req.args.get('offset')) # type: ignore
    limit = int(req.args.get('limit')) # type: ignore
    res = get_sorted_topics(limit=limit, offset=offset)
    return https_fn.Response(json.dumps(res).encode('utf-8'), mimetype="application/json")

@https_fn.on_request(timeout_sec=300, memory=options.MemoryOption.GB_1, cors=options.CorsOptions(
        cors_origins=[r"*"],
        cors_methods=["get"],
    ))
def fetch_supabase_topic_full(req: https_fn.Request) -> https_fn.Response:
    query = req.args.get('topic_id')
    success, res = find_topic_by_id(id=query) # type: ignore
    if not success:
        res = {"error": "sql query failed"}
    return https_fn.Response(json.dumps(res).encode('utf-8'), mimetype="application/json")

@https_fn.on_request(timeout_sec=300, memory=options.MemoryOption.GB_1, cors=options.CorsOptions(
        cors_origins=[r"*"],
        cors_methods=["get"],
    ))
def fetch_supabase_exercise_full(req: https_fn.Request) -> https_fn.Response:
    query = req.args.get('topic_id')
    success, res = find_topic_by_id(id=query) # type: ignore
    if success:
        exercises = []
        for exercise_id in set(res["exercises"]): # type: ignore
            exercise_success, exercise = find_exercise_by_id(id=exercise_id)
            if exercise_success:
                exercises.append(exercise)
        res = exercises
    else:
        res = {"error": "sql query failed"}
    return https_fn.Response(json.dumps(res).encode('utf-8'), mimetype="application/json")

@https_fn.on_request(timeout_sec=300, memory=options.MemoryOption.GB_1, cors=options.CorsOptions(
        cors_origins=[r"*"],
        cors_methods=["get"],
    ))
def fetch_recommendations(req: https_fn.Request) -> https_fn.Response:
    query = req.args.get('topic_id')
    num_recs = req.args.get('num_recs')
    success, res = find_topic_by_id(id=query) # type: ignore
    if success:
        topic_name = res["name"] # type: ignore
        res = recommender(base_topic=topic_name, num_results=num_recs) # type: ignore
    else:
        res = {"error": "sql query failed"}
    return https_fn.Response(json.dumps(res).encode('utf-8'), mimetype="application/json")

@scheduler_fn.on_schedule(schedule="0 * * * *", timeout_sec=300, memory=options.MemoryOption.GB_1) # type: ignore
def create_pipeline(event: scheduler_fn.ScheduledEvent) -> None:
    # Decrement all current topics
    decrement_internal_relevance_scores()
    # Runs whole pipeline
    topics = get_all_topics(source_limit=5)
    # Generates questions for topics
    for topic in topics:
        exercises = generate_mcqs_for_story(topic, num=3)
        for exercise in exercises:
            exercise_dict = exercise.to_dict()
            insert("generated_questions", exercise_dict)
        dict_topic = topic.get_dict()
        insert("topics", dict_topic)
