# YouTube Video Chat

A Streamlit application that enables users to chat with the content of YouTube videos using AI. This tool automatically extracts video transcripts and uses OpenAI to answer questions about the video content.

![YouTube Video Chat App](https://placeholder-for-screenshot.png)

## Features

- Extract transcripts directly from YouTube videos
- Chat with AI about the video content
- Maintain conversation history
- View raw transcript data
- Review OpenAI API interactions
- Clean, user-friendly interface

## Technologies Used

- **Streamlit**: For the web interface
- **Playwright**: For browser automation and transcript extraction
- **OpenAI API**: For AI-powered conversations
- **Hyperbrowser**: For managing browser sessions
- **Python**: Core programming language

## Prerequisites

- Python 3.7+
- OpenAI API key
- Hyperbrowser API key

## Installation

1. Clone this repository:
   ```bash
   git clone git@github.com:hyperbrowserai/examples.git
   cd chat-with/chat-with-youtube-video
   ```

2. Install required dependencies:
   ```bash
   pip install .
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   HYPERBROWSER_API_KEY=your_hyperbrowser_api_key
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run main.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (typically http://localhost:8501)

3. Enter a YouTube video URL in the input field

4. Ask questions about the video content in the chat interface

## How It Works

1. Playwright navigates to the video page and extracts the transcript
2. The transcript is processed and stored in the session state
3. When you ask a question, the application sends both the transcript and your question to OpenAI
4. The AI generates a response based on the video content
5. The conversation history is maintained for context in future questions

## Limitations

- The application requires videos to have available transcripts on YouTube
- AI responses are limited to the information available in the transcript
- The quality of responses depends on the accuracy and completeness of the transcript