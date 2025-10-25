import uuid
from datetime import datetime, timezone

class Exercise:
   def __init__(self, question: str, answer_choices: list[str], answer: int):
       self.id = str(uuid.uuid4())
       self.question = question
       self.answer_choices = answer_choices
       self.answer = answer
       self.date_created = datetime.now(timezone.utc)

   def to_dict(self):
       return {
           "id": self.id,
           "question": self.question,
           "answer_choices": self.answer_choices,
           "answer": self.answer,
           "date_created": self.date_created.isoformat()
       }

