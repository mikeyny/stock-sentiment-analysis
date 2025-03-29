import streamlit as st
import pandas as pd
import json
import time
from pathlib import Path

# Define the tickers you're tracking
TARGET_TICKERS = ['AAPL', 'TSLA', 'GOOG']

def load_data():
    """Load the most recent sentiment analysis results"""
    file_path = Path("./analyzed_data/sentiment_results.json")
    if file_path.exists():
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                st.error("Error parsing JSON file")  # Display error in the app
                return []
    else:
        st.warning("No sentiment data found.")  # Display warning in the app
        return []

def main():
    st.set_page_config(
        page_title="Stock Sentiment Dashboard",
        page_icon="📈",
        layout="wide"
    )

    # Add custom CSS
    st.markdown("""
    <style>
        .positive { color: #0f9d58; font-weight: bold; }
        .negative { color: #db4437; font-weight: bold; }
        .neutral { color: #f4b400; font-weight: bold; }
        .ticker { font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    st.title("Real-Time Stock Sentiment Analysis Dashboard")
    st.write("Aggregated sentiment scores for monitored tech stocks based on news articles.")

    # Auto-refresh settings
    with st.sidebar:
        st.title("Settings")
        refresh_interval = st.slider("Auto-refresh interval (seconds)", 5, 60, 10)
        auto_refresh = st.checkbox("Enable auto-refresh", value=True)

    # Load data from the JSON file
    data = load_data()
    
    if not data:
        st.warning("No sentiment data available yet.")
        return
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Display in columns
    cols = st.columns(len(df))
    
    for i, (_, row) in enumerate(df.iterrows()):
        ticker = row['ticker']
        sentiment = row['sentiment']
        article_count = row.get('article_count', 0)
        
        # Determine sentiment class
        sentiment_class = "neutral"
        sentiment_label = "NEUTRAL"
        if sentiment > 0.2:
            sentiment_class = "positive"
            sentiment_label = "BULLISH"
        elif sentiment < -0.2:
            sentiment_class = "negative"
            sentiment_label = "BEARISH"
        
        with cols[i]:
            st.markdown(f"<div class='ticker'>{ticker}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='{sentiment_class}'>Sentiment: {sentiment:.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='{sentiment_class}'>{sentiment_label}</div>", unsafe_allow_html=True)
            st.markdown(f"Based on {article_count} articles", unsafe_allow_html=True)
            
            # Create a simple visualization
            progress_value = (sentiment + 1) / 2  # Scale from -1:1 to 0:1
            st.progress(progress_value)
    
    # Show last update time
    st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main() 