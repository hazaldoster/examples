# Trend Summary Tool

A tool that aggregates trending topics from Hacker News and finds related discussions on Reddit to provide comprehensive trend summaries.

## What it does

This tool:

1. Opens Hacker News and finds the top post published today
2. Searches Reddit for discussions related to that Hacker News post
3. Identifies recent conversations and provides a summary of the discussions

## Requirements

- Node.js (v16 or higher recommended)
- A HyperBrowser API key (get your free key at [hyperbrowser.ai](https://hyperbrowser.ai))
- An OpenAI API key

## Setup

1. Clone this repository

```bash
git clone <repository-url>
cd Multipage-tool
```

2. Install dependencies

```bash
npm install
```

3. Create a `.env` file in the root directory with your API keys:

```
HYPERBROWSER_API_KEY=your_hyperbrowser_key_here
OPENAI_API_KEY=your_openai_key_here
```

## Usage

Run the script with:

```bash
npx ts-node TrendSummary.ts
```

## How it works

The tool uses HyperBrowser's AI agent capabilities to:

1. Navigate to Hacker News and identify the top trending post
2. Open a second browser page to search Reddit for related discussions
3. Analyze and summarize the discussions to provide insights

## Dependencies

- `@hyperbrowser/agent` (v0.3.1) & `@hyperbrowser/sdk` (v0.48.1): For browser automation with AI
- `@langchain/openai` (v0.5.10): For AI-powered content analysis
- `dotenv` (v16.5.0): For environment variable management
- `zod`: For schema validation
