
from scrape import get_all_topics
from question import generate_mcqs_for_story
from supabase_client import *

def create_pipeline():
    # Runs whole pipelin
    topics = get_all_topics(source_limit=1)
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

create_pipeline()