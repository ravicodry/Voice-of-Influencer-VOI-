import nltk
from textblob import TextBlob
import re

# Download required NLTK data
try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def analyze_sentiment(text):
    """Analyzes the sentiment of a given text using TextBlob."""
    try:
        analysis = TextBlob(text)
        # Get polarity (-1 to 1)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return "neutral"

def extract_keywords(text):
    """Extracts keywords using simple NLP techniques."""
    try:
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        
        # Get words and filter out common words
        words = text.split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'as', 'of'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return list(set(keywords))  # Return unique keywords
    except Exception as e:
        print(f"Error in keyword extraction: {e}")
        return []