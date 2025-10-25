
# DEPENDENCIES
from llama_index.llms.azure_openai import AzureOpenAI # Causes pydantic warning
from dotenv import load_dotenv
import os
import praw
from datetime import datetime, timezone
import uuid
import json
import json
from topic import Topic, get_utc_timestamp, parse_date
import requests
from bs4 import BeautifulSoup
import time

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

# For performance analysis
def timer(func):
    """
    A decorator that measures the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Record start time
        result = func(*args, **kwargs)    # Execute the wrapped function
        end_time = time.perf_counter()    # Record end time
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds.")
        return result
    return wrapper
    
# Ask llm to identify whether 
@timer
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
@timer
def prompt_about_url(prompt: str, url: str) -> str:
    context_response = requests.get(url)
    soup = BeautifulSoup(context_response.text, 'html.parser')
    condensed_content = " ".join(soup.text.split())
    response = NAVIGATOR_CLIENT.complete(
        prompt=f"Website context: {condensed_content}. Utilize the website content above for the provided prompt. Prompt: {prompt}")
    return str(response)

# Parse the actual topic based on website context
@timer
def parse_website_topic(url: str, name: str):
    summary_response = prompt_about_url(
        prompt="Summarize the following website into a short 100-150 word summary, provide the name of the tool, and provide a list of pros and cons. " \
        "Response should only contain JSON and look like:" \
        "{\"name\": \"name goes here\", \"summary\": \"summary goes here\", \"pros\": [\"pros goes here\"], \"cons\": [\"cons goes here\"]}", 
        url=url)
    summary_parsed = json.loads(summary_response)
    print(summary_parsed)
    return summary_parsed["name"], summary_parsed["summary"], summary_parsed["pros"], summary_parsed["cons"]

# Gets reddit posts
@timer
def get_reddit_posts(subreddit_name: str, limit: int, exceptions: list[str]) -> list[Topic]:
    # Gets subreddit
    subreddit = REDDIT_CLIENT.subreddit(subreddit_name)
    # Fetch posts
    topics = []
    for submission in subreddit.rising(limit=limit):
        valid, parsed_name = filter_post(topic=submission.title)
        if valid:
            filtered_name, summary, pros, cons = parse_website_topic(url=submission.url, name=parsed_name)
            valid_name = True # Check that it is not in exceptions
            for exception in exceptions:
                if exception.lower() in filtered_name.lower():
                    valid_name = False
            if valid_name:
                topic = Topic(
                    name=filtered_name,
                    url=submission.url,
                    summary=summary,
                    date_added=get_utc_timestamp(),
                    date_created=parse_date(submission.created_utc),
                    source="reddit",
                    is_archived=False, # Should always be false when first generated
                    is_active=True,
                    internal_relevance_score=0,
                    relevance_score=0,
                    exercises=[],
                    pros=pros,
                    cons=cons)
                topics.append(topic)
    return topics

@timer
def get_all_topics(source_limit: int = 10, exceptions: list[str] = ["reddit", 'github']) -> list[Topic]:
    relevant_subreddits = ["programming", "coding", "learnprogramming", "creativecoding"]
    all_topics = []
    for subreddit in relevant_subreddits:
        for item in get_reddit_posts(subreddit_name=subreddit, limit=source_limit, exceptions=exceptions):
            if item not in all_topics:
                all_topics.append(item)
    return all_topics

topics = get_all_topics(source_limit=5)
for topic in topics:
    print(topic.get_dict())




# 
response = NAVIGATOR_CLIENT.complete(prompt="Come up with a word ladder starting with the word CAR, having 7 words in the sequence, and ending with a 8 letter word. Return a JSON response.")
relevant_subreddits = ["programming", "coding", "learnprogramming", "creativecoding"]
for subreddit in relevant_subreddits:
    get_posts(subreddit_name=subreddit)

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
