import nltk
from textblob import TextBlob
import re
import warnings
from collections import Counter

# Suppress the specific warning
warnings.filterwarnings("ignore", category=SyntaxWarning, module="textblob")

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

def generate_summary(segments):
    """Generates a comprehensive summary of the video analysis."""
    try:
        # Combine all text
        all_text = ' '.join([seg['text'] for seg in segments])
        
        # Get overall sentiment
        sentiments = [seg['sentiment'] for seg in segments]
        sentiment_counts = Counter(sentiments)
        overall_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
        
        # Collect all positive and negative aspects
        positive_aspects = []
        negative_aspects = []
        for seg in segments:
            positive_aspects.extend(seg['good_aspect'])
            negative_aspects.extend(seg['bad_aspect'])
        
        # Get most common keywords
        all_keywords = []
        for seg in segments:
            all_keywords.extend(seg['keywords'])
        keyword_counts = Counter(all_keywords)
        top_keywords = [word for word, count in keyword_counts.most_common(10)]
        
        # Generate summary
        summary = {
            'overall_sentiment': overall_sentiment,
            'sentiment_distribution': dict(sentiment_counts),
            'positive_aspects': list(set(positive_aspects)),
            'negative_aspects': list(set(negative_aspects)),
            'top_keywords': top_keywords,
            'total_segments': len(segments),
            'summary_text': f"""
            Overall Analysis:
            - The video has an overall {overall_sentiment} sentiment
            - Analyzed {len(segments)} segments
            - Top keywords: {', '.join(top_keywords[:5])}
            
            Positive Points:
            {chr(10).join(['• ' + aspect for aspect in positive_aspects[:5]])}
            
            Areas of Concern:
            {chr(10).join(['• ' + aspect for aspect in negative_aspects[:5]])}
            """
        }
        
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None