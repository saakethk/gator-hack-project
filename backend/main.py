
# DEPENDENCIES
from llama_index.llms.azure_openai import AzureOpenAI
from dotenv import load_dotenv
import os
import praw
from datetime import datetime, timezone
import uuid
import json

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

# Story title
class Story:
    def __init__(self, name: str = "", url: str = "", source: str = "", 
                 date_created: float = 0, status: str = "", exercises: list[str] = [], relevance_score: int = 0, 
                 internal_relevance_score: int = 0):
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.url: str = url
        self.source: str = source
        self.date_added: datetime = self.get_utc_timestamp()
        self.date_created: datetime = self.parse_date(date_created)
        self.status: str = status
        self.exercises: list[str] = exercises
        self.relevance_score: int = relevance_score
        self.internal_relvance_score: int = internal_relevance_score
    def parse_date(self, utc_timestamp: float) -> datetime:
        return datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
    
    def get_utc_timestamp(self) -> float:
        utc_now = datetime.now(timezone.utc)
        return utc_now

# Gets reddit posts
def get_posts(subreddit_name: str):
    # Gets subreddit
    subreddit = REDDIT_CLIENT.subreddit(subreddit_name)
    # Fetch posts
    for submission in subreddit.rising(limit=100):
        print(f"Title: {submission.title}")
        print(f"Author: {submission.author}")
        print(f"URL: {submission.url}")
        print(f"Score: {submission.score}")
        print(f"Created (UTC): {submission.created_utc}")
        print(f"ID: {submission.id}")
        print("-" * 80)

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