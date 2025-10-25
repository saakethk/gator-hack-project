
from scrape import get_all_topics
from question import generate_mcqs_for_story

def create_pipeline():
    # Runs whole pipelin
    topics = get_all_topics(source_limit=2)
    # Generates questions for topics
    for topic in topics:
        exercises = generate_mcqs_for_story(topic, num=1)
        for exercise in exercises:
            topic.exercises.append(exercise.id)
        print(topic.get_dict())

create_pipeline()