
# DEPENDENCIES
from llama_index.llms.azure_openai import AzureOpenAI # Causes pydantic warning
from dotenv import load_dotenv
import os
import praw
from datetime import datetime, timezone
import uuid
import json
from topic import Topic, get_utc_timestamp, parse_date
import requests
from bs4 import BeautifulSoup
from exercise import Exercise

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

#fetches url content without ai stuff
def get_url_content(url:str):
    try:
        response = requests.get(url, timeout = 10)
        soup = BeautifulSoup(response.text, 'html.parser')

        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split(("  ")))
        condensed_content = ' '.join(chunk for chunk in chunks if chunk)

        return condensed_content
    except Exception as e:
        print(f"Error fetching URL content: {e}")
        return ""


print(prompt_about_url("Summarize the web page", "https://github.com/Old-Farmer/Mango-Editor"))


# 
# response = NAVIGATOR_CLIENT.complete(prompt="Come up with a word ladder starting with the word CAR, having 7 words in the sequence, and ending with a 8 letter word. Return a JSON response.")
# relevant_subreddits = ["programming", "coding", "learnprogramming", "creativecoding"]
# for subreddit in relevant_subreddits:
#     get_reddit_posts(subreddit_name=subreddit, limit )

#generates 1 mcq per topic in topics
def generate_mcqs_for_story(topic: Topic, num = 3):

    print(f"Fetching content from: {topic.url}")
    url_content = get_url_content(topic.url)

    if not url_content:
        print(f"Could not fetch content from URL, skipping MCQ generation")
        return []

    max_content_length = 3000
    if len(url_content) > max_content_length:
        url_content = url_content[:max_content_length] + "..."
        print(f"Content truncated to {max_content_length} characters")


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

    Topic: {topic.name}
    URL: {topic.url}
    
    Webpage Content (summarized for context):
    {url_content}
    
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
    
    Generate {num} questions now based on the scraped content provided.
    """

    try:
        response = NAVIGATOR_CLIENT.complete(prompt=prompt)

        cleaned = response.text.strip()
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        ai_response = json.loads(cleaned)

        exercises = []
        for question_data in ai_response["questions"]:
            exercise = Exercise(
                question=question_data["question"],
                answer_choices=question_data["choices"],
                answer=question_data["correct_answer"]
            )
            exercises.append(exercise)
            topic.exercises.append(exercise.id)

        return exercises

    except Exception as e:
        return []

if __name__ == "__main__":
    topics = get_all_topics(source_limit=2)

    for topic in topics:
        exercises = generate_mcqs_for_story(topic, num=1)

        if exercises:
            exercise = exercises[0]
            print(f"✓ QUESTION GENERATED:")
            print(f"Q: {exercise.question}")
            for choice in exercise.answer_choices:
                print(f"  {choice}")
            print(f"Correct Answer: {exercise.answer}")
        else:
            print("✗ Failed to generate MCQ for this topic")