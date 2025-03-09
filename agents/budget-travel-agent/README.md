# Google Travel Explorer

A Streamlit application that automates travel searches on Google Travel and uses OpenAI's Vision API to analyze the results.

## Features

- Automate searches on Google Travel Explore
- Set starting location, destination, and trip duration
- Take screenshots of the search results
- Analyze screenshots using OpenAI's Vision API to extract:
  - Travel dates
  - Travel costs
  - Travel times
  - Accommodation costs

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```
4. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the Streamlit app:
```bash
streamlit run main.py
```

Then:
1. Enter your starting location
2. Enter your destination
3. Select your desired trip duration (Weekend, 1 Week, or 2 Weeks)
4. Click "Search Travel Options"

The app will then:
- Navigate to Google Travel
- Enter your search parameters
- Take a screenshot of the results
- Analyze the screenshot using OpenAI
- Display the extracted information

## Requirements

- Python 3.8+
- Streamlit
- Playwright
- OpenAI API key
- Python-dotenv
