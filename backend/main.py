
# DEPENDENCIES
from llama_index.llms.azure_openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json
import praw
from datetime import datetime, timezone
import uuid
from topic import Topic, get_utc_timestamp, parse_date
import requests
from bs4 import BeautifulSoup
from supabase_client import *

#from supabase import create_client, Client

load_dotenv()



# Authenticate with API
NAVIGATOR_AI_KEY = os.getenv("NAVIGATOR_AI_TOOLKIT")
NAVIGATOR_CLIENT = AzureOpenAI(
    engine="llama-3.3-70b-instruct",
    temperature=0.0,
    azure_endpoint="https://api.ai.it.ufl.edu",
    api_key=NAVIGATOR_AI_KEY,
    api_version="2023-07-01-preview",
)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_CLIENT = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="my_reddit_scraper/1.0 by u/Capital-Olive1823"
)

# Ask llm to identify whether 
def filter_post(topic: str) -> tuple[bool, str]:
    response = NAVIGATOR_CLIENT.complete(
        prompt=f"The title of a post is {topic}. Your role is to identify whether this title contains a software technology or is irrelevant. " \
        "Return a json response with the key 'relevant' which has true or false and extract just the name of the technology under the key 'name'. Response should only contain JSON and look like:" \
        "{'relevant': false, 'name': 'python'}")
    try:
        response_parsed = json.loads(str(response))
        if response_parsed["name"] != "" and response_parsed["name"] != None:
            return response_parsed["relevant"], response_parsed["name"]
        else:
            return False, response_parsed["name"]
    except Exception as error:
        return False, str(error)
    
# Parse the url to make 
def prompt_about_url(prompt: str, url: str) -> str:
    context_response = requests.get(url)
    soup = BeautifulSoup(context_response.text, 'html.parser')
    condensed_content = " ".join(soup.text.split())
    response = NAVIGATOR_CLIENT.complete(
        prompt=f"Website context: {condensed_content}. Utilize the website content above for the provided prompt. Prompt: {prompt}")
    return str(response)

# Gets reddit posts
def get_reddit_posts(subreddit_name: str, limit: int) -> list[Topic]:
    # Gets subreddit
    subreddit = REDDIT_CLIENT.subreddit(subreddit_name)
    # Fetch posts
    topics = []
    for submission in subreddit.rising(limit=limit):
        valid, parsed_name = filter_post(topic=submission.title)
        if valid:
            topic = Topic(
                name=parsed_name,
                url=submission.url,
                summary="",
                date_added=get_utc_timestamp().timestamp(), # CONVERTING TO UNIX TIMESTAMP
                date_created=parse_date(submission.created_utc).timestamp(), # CONVERTING TO UNIX TIMESTAMP
                source="reddit",
                is_archived=False, # Should always be false when first generated
                is_active=True,
                internal_relevance_score=0,
                relevance_score=submission.score,
                exercises=[])
            insert_topic(topic_data=topic.get_dict())
            topics.append(topic)
        
    return topics

def get_all_topics(source_limit: int = 10) -> list[Topic]:
    relevant_subreddits = ["programming", "coding", "learnprogramming", "creativecoding"]
    all_topics = []
    for subreddit in relevant_subreddits:
        for item in get_reddit_posts(subreddit_name=subreddit, limit=source_limit):
            if item not in all_topics:
                all_topics.append(item)
    return all_topics

# topics = get_all_topics(source_limit=5)
# for topic in topics:S
#     print(topic.url)


def generate_mcqs_for_story(story, num = 3):
    prompt = f"""
    Act as a college professor creating an application for a 
    computer science learning platform, who specializes in 
    condensing difficult problems into easy-to-understand ideas.
    Help me create multiple choice questions that test a user's understanding
    at a surface level. These questions should stick to the core of the topic,
    but maintain a level of simplicity that simply helps the user get a
    grasp of the surface level. By the end of the question, the user should have an idea
    of the topic, how it can become more complex despite the questions simplicity, and understand something new about the topic.
        
    Step 1: Analyze the story name and fetch the story from its url.
    Step 2: Based on your understanding of this topic, as a college professor who can easily explain complex subjects, come up with a fundamental easy question that can be asked to the user utilizing the consequent requirements.
    Step 3: Create {num} multiple choice questions about the following topic with the requirements that will follow in mind.

    Topic: {story.name}
    URL: {story.url}
    
    REQUIREMENTS:
    - Questions should be EASY and test surface-level understanding
    - Questions should help users grasp basic concepts about the topic
    - Each question should have 4 answer choices (A, B, C, D)
    - Mark the correct answer clearly
    - Questions should be practical and conceptual, not trivia
    - Avoid overly technical jargon
    - Make questions engaging and educational
    
    IMPORTANT: Return ONLY valid JSON in this exact format:
    {{
        "questions": [
            {{
                "question": "Question text here?",
                "choices": [
                    "A) First choice",
                    "B) Second choice",
                    "C) Third choice",
                    "D) Fourth choice"
                ],
                "correct_answer": "A"
            }}
        ]
    }}
    
    Generate {num} questions now.
    """

    try:
        response = NAVIGATOR_CLIENT.complete(prompt=prompt)

        ai_response = json.loads(response.text.strip())

        exercises = []


    except Exception as e:
        print(f"Error generating MCQs for {story.name}: {e}")


#relevant_subreddits = ["programming", "coding", "learnprogramming", "creativecoding"]
# for subreddit in relevant_subreddits:
#     get_reddit_posts(subreddit_name=subreddit, limit=10)

# print(get_info_about_topic("name", "source", "relevance_score"))

