from dotenv import load_dotenv
import os
import praw

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

# Authenticate with Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="my_reddit_scraper/1.0 by u/Capital-Olive1823"
)

# Choose the subreddit
subreddit_name = "python"
subreddit = reddit.subreddit(subreddit_name)

# Fetch posts (e.g., from 'hot', 'new', or 'top')
for submission in subreddit.hot(limit=100):  # limit=None will stream indefinitely
    print(submission)
    print(f"Title: {submission.title}")
    print(f"Author: {submission.author}")
    print(f"URL: {submission.url}")
    print(f"Score: {submission.score}")
    print(f"Created (UTC): {submission.created_utc}")
    print(f"ID: {submission.id}")
    print("-" * 80)