import streamlit as st
import pandas as pd
from src.youtube_utils import get_transcript, get_video_details
from src.llm_utils import analyze_with_llm
from src.storage_utils import save_segment_product_analysis, load_segment_product_analysis
from src.nlp_utils import analyze_sentiment, extract_keywords
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Voice of influencer", layout="wide")
st.title("🎥 YouTube Product Review Analyzer")

video_url = st.text_input("Enter YouTube Video URL:")

# Sidebar for User-Defined Product
st.sidebar.header("Product to Analyze")
user_defined_product = st.sidebar.text_input("Enter the Product Name:")

def filter_keywords(keywords):
    """Filters common and less relevant keywords."""
    stop_words = [
        "people", "thing", "it", "they", "he", "she", "we", "you", "i",
        "the", "a", "an", "this", "that", "these", "those", "here", "there",
        "be", "have", "do", "say", "go", "will", "would", "can", "could",
        "may", "might", "should", "get", "make", "know", "think", "take",
        "see", "come", "look", "use", "one", "two", "three", "four", "five",
        "year", "years", "month", "months", "day", "days", "time", "lot",
        "bit", "kind", "sort", "way", "something", "anything", "everything",
        "nothing", "someone", "anyone", "everyone", "noone", "well", "really",
        "very", "pretty", "quite", "just", "even", "still", "however",
        "also", "too", "much", "many", "good", "bad", "overall", "experience",
        "feel", "seem", "look",
        # Add more based on your observations
    ]
    filtered_keywords = []
    for keyword in keywords:
        if isinstance(keyword, str) and keyword.lower() not in stop_words:
            filtered_keywords.append(keyword)
    return filtered_keywords

def generate_wordcloud(text, title):
    """Generates and displays a word cloud."""
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.subheader(title)
    st.pyplot(fig)

if st.button("Analyze"):
    if not video_url:
        st.error("Please enter a valid YouTube URL.")
    elif not user_defined_product:
        st.error("Please enter the name of the product you want to analyze in the sidebar.")
    else:
        with st.spinner("Fetching transcript..."):
            transcript_list, error = get_transcript(video_url)

        if error:
            st.error(error)
        elif not transcript_list:
            st.error("No transcript available for this video. Analysis cannot proceed.")
        else:
            st.success("Transcript fetched successfully!")

            analyzed_segments = []
            with st.spinner("Analyzing segments..."):
                for segment in transcript_list:
                    text = segment['text']
                    start_time = segment['start']
                    end_time = segment['start'] + segment['duration']

                    sentiment = analyze_sentiment(text)
                    keywords = filter_keywords(extract_keywords(text))
                    good_aspect = []
                    bad_aspect = []

                    if sentiment == "positive":
                        if any(word in text.lower() for word in ["love", "great", "amazing", "easy", "best"]):
                            good_aspect.extend(keywords)
                    elif sentiment == "negative":
                        if any(word in text.lower() for word in ["problem", "difficult", "bad", "worst", "issue"]):
                            bad_aspect.extend(keywords)

                    analyzed_segments.append({
                        'video_url': video_url,
                        'video_title': 'N/A',
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': text,
                        'sentiment': sentiment,
                        'keywords': keywords,
                        'good_aspect': list(set(good_aspect)),
                        'bad_aspect': list(set(bad_aspect)),
                        'product_name': user_defined_product.strip() # Use user-defined product name
                    })

            with st.spinner("Fetching video details..."):
                details, error_details = get_video_details(video_url)
                if details:
                    for segment in analyzed_segments:
                        segment['video_title'] = details['title']

            if error_details:
                st.error(error_details)
            else:
                st.success("Video details fetched successfully!")
                with st.spinner("Saving segment-level analysis..."):
                    save_segment_product_analysis(analyzed_segments)
                    st.success("Segment-level analysis complete and saved! ✅")

st.sidebar.header("Filter by Product")
all_analyzed_segments = load_segment_product_analysis()
all_products = ["All Products"]
if all_analyzed_segments:
    # Dynamically generate product list based on user input during analysis
    unique_products = set(seg.get('product_name', 'N/A') for seg in all_analyzed_segments)
    all_products.extend(sorted(list(unique_products)))

selected_product = st.sidebar.selectbox("Select Product:", all_products)

st.subheader("📊 Product Review Dashboard")

filtered_segments = all_analyzed_segments
if selected_product != "All Products" and all_analyzed_segments:
    filtered_segments = [seg for seg in all_analyzed_segments if seg.get('product_name', '').lower() == selected_product.lower()] # Case-insensitive filtering

df = pd.DataFrame(filtered_segments)

if not df.empty:
    st.subheader(f"Reviews for: {selected_product if selected_product != 'All Products' else 'All Products'}")

    # Sentiment Distribution (Positive and Negative Only)
    sentiment_counts = df['sentiment'].value_counts()
    sentiment_to_display = sentiment_counts[sentiment_counts.index.isin(['positive', 'negative'])]
    if not sentiment_to_display.empty:
        st.subheader("Sentiment Distribution (Positive & Negative)")
        st.bar_chart(sentiment_to_display)
    else:
        st.info("No positive or negative sentiment found for the selected product.")

    def get_top_keywords(sentiment_df, n=10):
        all_keywords = sentiment_df['keywords'].explode().tolist()
        filtered_keywords = filter_keywords(all_keywords)
        return pd.Series(filtered_keywords).value_counts().nlargest(n)

    # Top Positive Keywords
    positive_df = df[df['sentiment'] == 'positive']
    if not positive_df.empty and 'keywords' in positive_df.columns:
        top_positive_keywords = get_top_keywords(positive_df)
        st.subheader("Top Positive Keywords")
        st.bar_chart(top_positive_keywords)
        generate_wordcloud(" ".join(positive_df['keywords'].astype(str)), "Positive Sentiment Word Cloud")
    else:
        st.info("No positive reviews or keywords found for the selected product.")

    # Top Negative Keywords
    negative_df = df[df['sentiment'] == 'negative']
    if not negative_df.empty and 'keywords' in negative_df.columns:
        top_negative_keywords = get_top_keywords(negative_df)
        st.subheader("Top Negative Keywords")
        st.bar_chart(top_negative_keywords)
        generate_wordcloud(" ".join(negative_df['keywords'].astype(str)), "Negative Sentiment Word Cloud")
    else:
        st.info("No negative reviews or keywords found for the selected product.")

    if st.checkbox(f"Show Raw Analyzed Segments for '{selected_product if selected_product != 'All Products' else 'All Products'}'"):
        st.dataframe(df)
else:
    st.info("No product reviews analyzed yet.")