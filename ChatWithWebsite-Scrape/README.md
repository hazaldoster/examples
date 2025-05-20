# Chat With Any Website

Welcome to Chat With Any Website, an official example project powered by the [Hyperbrowser API](https://hyperbrowser.ai/)! This tool demonstrates how easy it is to leverage Hyperbrowser's advanced web scraping capabilities and combine them with OpenAI's conversational AI—all from your terminal.


👉 **Get your free API key today at [hyperbrowser.ai](https://hyperbrowser.ai/)!**

## Features

- Scrape any webpage using the Hyperbrowser SDK
- Chat with an OpenAI-powered assistant about the scraped content
- Simple command-line interface

## Requirements

- Node.js (v18 or higher recommended)
- npm or yarn
- API keys for [Hyperbrowser](https://hyperbrowser.ai/) and [OpenAI](https://platform.openai.com/)

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ChatWithWebsite-Scrape
   ```
2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```
3. **Set up your API keys:**
   - Sign up at [hyperbrowser.ai](https://hyperbrowser.ai/) to get your free Hyperbrowser API key.
   - Get your OpenAI API key from [platform.openai.com](https://platform.openai.com/).
   - Create a `.env` file in the root directory with the following content:
     ```env
     HYPERBROWSER_API_KEY=your_hyperbrowser_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

## Usage

Run the script using ts-node or compile it with tsc:

```bash
npx ts-node scrapechat.ts
```

- Enter the URL you want to scrape when prompted.
- Chat with the AI about the page content. Type `exit` to quit.

## Notes

- Make sure your API keys have sufficient quota.
- This tool is for educational and personal use. Please respect website terms of service when scraping.
- For more advanced scraping, batch jobs, or custom integrations, check out the [Hyperbrowser API docs](https://hyperbrowser.ai/docs).

## About Hyperbrowser

Hyperbrowser is trusted by developers and enterprises worldwide for real-time, reliable web data extraction. Our mission is to make the web programmable for everyone. Join our community and supercharge your projects with the best web scraping API available!

👉 **Sign up now and get started for free at [hyperbrowser.ai](https://hyperbrowser.ai/)!**

## License

MIT
