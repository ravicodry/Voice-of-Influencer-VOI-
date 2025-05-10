import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import spacy

# Download required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# Initialize the analyzer
analyzer = SentimentIntensityAnalyzer()

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not downloaded, download it
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def analyze_sentiment(text):
    """Analyzes the sentiment of a given text."""
    vs = analyzer.polarity_scores(text)
    if vs['compound'] >= 0.05:
        return "positive"
    elif vs['compound'] <= -0.05:
        return "negative"
    else:
        return "neutral"

def extract_keywords(text):
    """Extracts noun keywords from a given text and returns their lemmas."""
    doc = nlp(text)
    keywords = [token.lemma_.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop]
    return list(set(keywords)) # Return unique lemmas