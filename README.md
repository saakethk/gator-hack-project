# gator-hack-project
The idea is to create a educational website that targets the computer science domain. Its meant to help allow people to learn about new technologies and try them out in a quick and effective way opposed to spending hours googling. Targets new repos and emerging technologies.

## Things To Implement
- Scraping
- Pro's & Cons
- Generated Exercises

## Database Schemas
Topic
id: str
name: str
url: str
summary: str
source: str
date_added: str
date_created: str
is_active: bool,
is_archived: bool,
exercises: list[str]
relevance_score: int
internal_relvance_score

Exercises
id: str
question: str
answer_choices: list[str]
answer: str
date_created: str

User
id: str
completed_exercises: str
topics_visited: str
date_joined: str

## Sources
1) https://praw.readthedocs.io/en/stable/
2) https://developers.llamaindex.ai/python/framework/
3) https://supabase.com/docs/reference/python/installing
