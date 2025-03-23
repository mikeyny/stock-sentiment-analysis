# Stock Sentiment Analysis

A real-time sentiment analysis system for financial markets that helps traders make informed buy/sell decisions based on news sentiment.

## Overview

This project demonstrates how to build a real-time sentiment analysis system that ingests financial news from Yahoo Finance, analyzes sentiment, and visualizes trading signals.

## Repository Structure

- **config.yaml**: Configuration file for [Redpanda Connect](https://docs.redpanda.com/redpanda-connect/home/) that defines how to fetch financial news from Yahoo Finance and transform it into structured data and sends it to a RedPanda topic.

- **sentiment_processor.py**: Core processing script that:
  - Consumes news articles from Redpanda
  - Analyzes sentiment using TextBlob
  - Aggregates sentiment by stock ticker
  - Persists results to JSON for visualization

- **stock_dashboard.py**: Streamlit dashboard that:
  - Displays real-time sentiment for monitored stocks
  - Provides buy/sell/hold signals based on sentiment thresholds
  - Auto-refreshes to show the latest data

## Getting Started

See the full tutorial at [Buy or Sell Stocks Using Sentiment Analysis](https://redpanda.com/blog) for detailed setup instructions and explanation of how the system works.

## Quick Start

1. Create a virtual environment and install dependencies
2. Set up Redpanda and Redpanda Connect
3. Run the sentiment processor:
   ```bash
   python sentiment_processor.py
   ```

4. Launch the Streamlit dashboard:
   ```bash
   streamlit run stock_dashboard.py
   ```

For complete instructions, refer to the tutorial.

