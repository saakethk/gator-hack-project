
from bs4 import BeautifulSoup
import requests
from topic import Topic
import json
from general import NAVIGATOR_CLIENT
from exercise import Exercise
from scrape import get_all_topics

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

#generates 1 mcq per topic in topics
def generate_mcqs_for_story(topic: Topic, num: int = 3):

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

def test_question():
   
   topics = get_all_topics(source_limit=2)
   for topic in topics:
       exercises = generate_mcqs_for_story(topic, num=1)

       if exercises:
           exercise = exercises[0]
           print(f"QUESTION GENERATED:")
           print(f"Q: {exercise.question}")
           for choice in exercise.answer_choices:
               print(f"  {choice}")
           print(f"Correct Answer: {exercise.answer}")
       else:
           print("Failed to generate MCQ for this topic")

# test_question()
