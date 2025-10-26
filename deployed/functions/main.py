""" Gets all relevant api keys and such for api calls """

# Dependencies
from firebase_functions import https_fn, scheduler_fn, options
from firebase_admin import initialize_app
from scraper import get_all_topics
from excercise_generator import generate_mcqs_for_story
from database import insert, get_sorted_topics
from chat import chatbot

initialize_app()

@https_fn.on_request()
def chat_request(req: https_fn.Request) -> https_fn.Response:
    query = req.args.get('query')
    topic = req.args.get('topic')
    history = req.args.get('history')
    res = chatbot(user_input=query, topic=topic, history=history)
    return https_fn.Response(res)

@https_fn.on_request()
def fetch_supabase_topics(req: https_fn.Request) -> https_fn.Response:
    offset = int(req.args.get('offset'))
    limit = int(req.args.get('limit'))
    res = get_sorted_topics(limit=limit, offset=offset)
    return https_fn.Response(res)

@scheduler_fn.on_schedule(schedule="0 * * * *", timeout_sec=300, memory=options.MemoryOption.GB_1) # type: ignore
def create_pipeline(event: scheduler_fn.ScheduledEvent) -> None:
    # Runs whole pipeline
    topics = get_all_topics(source_limit=5)
    # Generates questions for topics
    for topic in topics:
        exercises = generate_mcqs_for_story(topic, num=1)
        for exercise in exercises:
            exercise_dict = exercise.to_dict()
            insert("generated_questions", exercise_dict)
            topic.exercises.append(exercise.id)
        dict_topic = topic.get_dict()
        insert("topics", dict_topic)
        print(dict_topic)
