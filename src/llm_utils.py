import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_with_llm(transcript_text):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes YouTube videos."},
                {"role": "user", "content": f"Analyze the following transcript:\n\n{transcript_text}\n\nGive:\n1. Summary\n2. Sentiment\n3. Keywords"}
            ],
            temperature=0.5,
            max_tokens=1000,
        )
        analysis_text = response.choices[0].message.content
        return analysis_text, None
    except Exception as e:
        return None, f"❌ Error with OpenAI API: {str(e)}"