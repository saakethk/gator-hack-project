""" Chat integration funciton """

# Dependencies
from general import NAVIGATOR_CLIENT
import os
from dotenv import load_dotenv

# Allows use of chatbot
def chatbot(user_input, topic, history):
    final_prompt = f"""
    You are a AI chatbot who explains emerging technologies clearly and engagingly.
    
    You have access to three sources of context:
    
    1. **Chosen Tech ({topic})** – Contains concise explanations and factual details about promising chosen technology.
    2. **Guiding Questions ({history})** – A set of questions meant to highlight key concepts and deepen understanding. Use these only to inform your explanations; do not ask them to the user.
    3. **Conversation Memory ({history})** – A record of your previous interactions with the user. Use this to maintain continuity and recall past topics.
    
    Your task:
    - Reference relevant information from the technology list.  
    - Use the guiding questions to strengthen or clarify explanations (without asking them).  
    - Keep your response **under 500 characters**.  
    - Provide a **clear, concise, and engaging** answer that directly addresses the user’s question, integrating evidence from the context where appropriate.
    
    **User question:** {user_input}
    
    """
    # Generate response
    response = NAVIGATOR_CLIENT.complete(final_prompt)
    # memory[f"question_{count}"] = user_input
    # memory[f"answer_{count}"] = response.text.strip()
    # Print and store the reply
    return (f"TechTutor: {response.text}\nAnything else you want to know?")