from textblob import TextBlob
from bytewax.dataflow import Dataflow
from bytewax.connectors.kafka import KafkaSource
from bytewax.testing import run_main
import bytewax.operators as op
import json
import os
from datetime import datetime
from pathlib import Path

# Constants and global state
KAFKA_BROKER = "localhost:9092"
INPUT_TOPIC = "raw_articles"
OUTPUT_DIR = Path("./analyzed_data")
TARGET_TICKERS = ["AAPL", "TSLA", "GOOG"]

# Global dictionary for state
RESULTS = {}

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_article(article):
    """Process a message containing news articles"""
    try:
        # Extract the message value from KafkaSourceMessage
        if hasattr(article, 'value'):
            # Decode bytes to string if needed
            message_value = article.value
            if isinstance(message_value, bytes):
                message_value = message_value.decode('utf-8')
            
            # Parse the JSON string into a list of articles
            try:
                articles_list = json.loads(message_value)
            except json.JSONDecodeError:
                print(f"Failed to parse message as JSON: {message_value[:100]}...")
                return []
            
            # Process each article in the list
            results = []
            for article_data in articles_list:
                try:
                    # Extract article content
                    title = article_data.get("title", "")
                    description = article_data.get("description", "")
                    text = f"{title}. {description}"
                    
                    # Skip empty articles
                    if not text.strip():
                        continue
                    
                    # Calculate sentiment using TextBlob
                    blob = TextBlob(text)
                    sentiment = blob.sentiment.polarity
                    
                    # Check which target tickers are mentioned
                    mentioned_tickers = []
                    for ticker in TARGET_TICKERS:
                        if ticker in title or ticker in description:
                            mentioned_tickers.append(ticker)
                    
                    if not mentioned_tickers:
                        continue

                    # Add results for each mentioned ticker
                    for ticker in mentioned_tickers:
                        results.append((ticker, sentiment))
                        
                except Exception as e:
                    print(f"Error processing article: {str(e)}")
                    continue
                    
            return results
        else:
            return []
            
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return []

def save_results():
    """Save the current results to JSON file"""
    with open(OUTPUT_DIR / "sentiment_results.json", "w") as f:
        json.dump(list(RESULTS.values()), f, indent=2)

def create_dataflow():
    """Create the Bytewax dataflow pipeline"""
    flow = Dataflow("sentiment-analysis")
    
    source = KafkaSource([KAFKA_BROKER ], [INPUT_TOPIC])
    
    # Build the processing pipeline
    inp = op.input("input", flow, source)
    
    # Process articles and extract sentiment
    processed = op.map("process", inp, process_article)
    flattened = op.flat_map("flatten", processed, lambda x: x)
    
    # Group by ticker
    keyed = op.key_on("key", flattened, lambda x: x[0])
    
    def update_state(state, value):
        if state is None:
            state = (0, 0.0)  # (count, sum_sentiment)
        
        count, total = state
        ticker, sentiment = value
        
        new_count = count + 1
        new_total = total + sentiment
        new_state = (new_count, new_total)
        
        # Calculate average sentiment
        avg_sentiment = new_total / new_count
        
        # Store result
        RESULTS[ticker] = {
            "ticker": ticker,
            "sentiment": avg_sentiment,
            "article_count": new_count,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Updated sentiment for {ticker}: {avg_sentiment:.2f} based on {new_count} articles")
        save_results()
        
        return (new_state, new_state)
    
    # Use stateful_map
    results = op.stateful_map("update_state", keyed, update_state)
    
    # Required terminal step
    op.inspect("print_results", results, lambda step_id, item: None)
    
    return flow

if __name__ == "__main__":
    flow = create_dataflow()
    run_main(flow)