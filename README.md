# gator-hack-project
The idea is to create a educational website that targets the computer science domain. Its meant to help allow people to learn about new technologies and try them out in a quick and effective way opposed to spending hours googling. Targets new repos and emerging technologies.

## Things To Implement
- Scraping
- Pro's & Cons
- Generated Exercises

## API Endpoints

1) https://chat-request-xvt4z5lyxa-uc.a.run.app
    - GET
    - Params
        - query: str - user query
        - topic: str - topic for context
        - history: JSON string array - user and llm conversation history
    - Returns:
        - string response

2) https://fetch-supabase-topics-xvt4z5lyxa-uc.a.run.app
    - GET
    - Params:
        - offset: int - starting index from which to start counting
        - limit: int - max number of topics to return
    - Returns:
        - Array of Truncated Topics
            - id: str - associated database id
            - name: str - name of topic
            - internal_relevance_score: int - internal relevance metric
            - relevance_score: int - external relevance metric
            - date_added: str - date added to our database

3) https://fetch-supabase-topic-full-xvt4z5lyxa-uc.a.run.app
    - GET
    - Params:
        - topic_id: str - corresponding database id of topic to pull
    - Returns:
        - Singular Topic Object

4) https://fetch-supabase-exercise-full-xvt4z5lyxa-uc.a.run.app
    - GET
    - Params:
        - topic_id: str - corresponding database id of topic to pull
    - Returns:
        - Array of Exercise Objects

## Database Schemas
- Topic
    - id: str
    - name: str
    - url: str
    - summary: str
    - source: str
    - date_added: str
    - date_created: str
    - is_active: bool,
    - is_archived: bool,
    - exercises: list[str]
    - relevance_score: int
    - internal_relvance_score

- Exercises
    - id: str
    - question: str
    - answer_choices: list[str]
    - answer: int
    - date_created: str

- User
    - id: str
    - completed_exercises: list[str]
    - topics_visited: list[str]
    - date_joined: str

## Sources
1) https://praw.readthedocs.io/en/stable/
2) https://developers.llamaindex.ai/python/framework/
3) https://supabase.com/docs/reference/python/installing
