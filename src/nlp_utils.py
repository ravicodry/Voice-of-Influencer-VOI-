import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import sys

# Download required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# Initialize the analyzer
analyzer = SentimentIntensityAnalyzer()

# Initialize spaCy lazily
nlp = None

def get_spacy_model():
    global nlp
    if nlp is None:
        try:
            import spacy
            try:
                nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Downloading spaCy model...")
                spacy.cli.download("en_core_web_sm")
                nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Error loading spaCy model: {e}")
            return None
    return nlp

def analyze_sentiment(text):
    """Analyzes the sentiment of a given text."""
    try:
        vs = analyzer.polarity_scores(text)
        if vs['compound'] >= 0.05:
            return "positive"
        elif vs['compound'] <= -0.05:
            return "negative"
        else:
            return "neutral"
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return "neutral"

def extract_keywords(text):
    """Extracts noun keywords from a given text and returns their lemmas."""
    try:
        spacy_model = get_spacy_model()
        if spacy_model is None:
            return []
        
        doc = spacy_model(text)
        keywords = [token.lemma_.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop]
        return list(set(keywords))  # Return unique lemmas
    except Exception as e:
        print(f"Error in keyword extraction: {e}")
        return []