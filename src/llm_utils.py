import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def analyze_with_llm(text):
    """Analyzes text using OpenAI's API."""
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes product reviews."},
                {"role": "user", "content": f"Analyze this product review: {text}"}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in LLM analysis: {e}")
        return None