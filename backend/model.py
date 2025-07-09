import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import os

OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def generate_answer(query, context):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4"-
        messages=[  
            {"role": "system", "content": "You are an AI assistant that provides answers based on provided context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
    )
    return response.choices[0].message.content
