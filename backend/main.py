
# DEPENDENCIES
from llama_index.llms.azure_openai import AzureOpenAI # Causes pydantic warning
from dotenv import load_dotenv
import os
import praw
import json
from topic import Topic, get_utc_timestamp, parse_date
import requests
from bs4 import BeautifulSoup

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
                date_added=get_utc_timestamp(),
                date_created=parse_date(submission.created_utc),
                source="reddit",
                is_archived=False, # Should always be false when first generated
                is_active=True,
                internal_relevance_score=0,
                relevance_score=0,
                exercises=[])
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
# for topic in topics:
#     print(topic.url)

print(prompt_about_url("Summarize the web page", "https://github.com/Old-Farmer/Mango-Editor"))


