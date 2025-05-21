# GitHub Profile Analyzer

This tool analyzes GitHub profiles to extract information about a user's tech stack, programming languages, frameworks, tools, and repositories.

## Features

- Extracts primary programming languages used
- Identifies frameworks and tools in repositories
- Lists and summarizes top repositories
- Handles GitHub profile analysis with captcha solving

## Prerequisites

- Node.js and npm installed
- HyperBrowser API key (get yours at [hyperbrowser.ai](https://hyperbrowser.ai))

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file in the project root with your API key:
   ```
   HYPERBROWSER_API_KEY=your_api_key_here
   ```

## Usage

Run the tool with:

```
npm start
```

You'll be prompted to enter a GitHub username, and the tool will analyze their profile and display the results.

## How It Works

This tool uses HyperBrowser's extraction capabilities to analyze GitHub profiles by:

1. Navigating to the user's GitHub page
2. Using AI to extract structured information about their repositories and tech stack
3. Returning the data in a structured JSON format

## Dependencies

- [@hyperbrowser/sdk](https://www.npmjs.com/package/@hyperbrowser/sdk) - HyperBrowser SDK
- [dotenv](https://www.npmjs.com/package/dotenv) - Environment variable management
- [zod](https://www.npmjs.com/package/zod) - Schema validation
