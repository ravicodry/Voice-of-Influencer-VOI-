import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import spacy

# Download VADER lexicon if you haven't already
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    nltk.download('vader_lexicon')

analyzer = SentimentIntensityAnalyzer()
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