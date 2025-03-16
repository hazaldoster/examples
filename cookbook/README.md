# YouTube Video Chat - Jupyter Notebook

This Jupyter notebook allows you to analyze and chat with the content of any YouTube video using AI. It extracts the transcript from a YouTube video and uses OpenAI to generate responses to questions about the video content.

## Requirements

Before using this notebook, you'll need to install the following dependencies:

```bash
pip install openai playwright python-dotenv jupyter hyperbrowser
```

You'll also need to install Playwright's browser dependencies:

```bash
python -m playwright install chromium
```

## Configuration

Create a `.env` file in the same directory as the notebook with the following environment variables:

```
OPENAI_API_KEY=your_openai_api_key
HYPERBROWSER_API_KEY=your_hyperbrowser_api_key
```

You can get a Hyperbrowser API key from [hyperbrowser.ai](https://hyperbrowser.ai).

## Usage

1. Run the notebook cells in sequence
2. Enter your YouTube URL in the designated cell
3. The notebook will extract the video transcript
4. You can then ask questions about the video content in the question cells
5. Add new cells as needed for additional questions

## Features

- Extracts YouTube video transcripts with timestamps
- Uses OpenAI to answer questions about video content
- Maintains conversation context through chat history
- Displays the full transcript for reference
- Minimizes interactivity with user parameters at the start
