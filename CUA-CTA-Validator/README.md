# CUA-CTA-Validator

A tool that uses Hyperbrowser's Conversational User Agent (OPENAI CUA) to validate and analyze Call-to-Action (CTA) buttons on websites.

## Description

This tool automatically identifies the main CTA button in a website's hero section and performs a comprehensive analysis of its accessibility and SEO characteristics. It then provides specific improvement suggestions based on this analysis.

## Features

- Automatically identifies the main CTA button in a website's hero section
- Analyzes CTA buttons for accessibility and SEO best practices
- Checks color contrast, text clarity, and positioning
- Provides 3-5 specific improvement suggestions

## Requirements

- Node.js
- Hyperbrowser API key (get your API keys at hyperbrowser.ai)

## Installation

1. Clone the repository
2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file in the root directory with your Hyperbrowser API key:

```
HYPERBROWSER_API_KEY=your_api_key_here
```

## Usage

Run the validator by providing a URL as a command-line argument:

```bash
npm start -- https://example.com
```

Or run without arguments to be prompted for a URL:

```bash
npm start
```

## How It Works

1. The tool connects to the Hyperbrowser API using your API key
2. It navigates to the specified URL
3. Step 1: Identifies the main CTA button in the hero section
4. Step 2: Analyzes the CTA for accessibility and SEO best practices
5. Step 3: Generates specific improvement suggestions

## Dependencies

- @hyperbrowser/sdk - For interacting with Hyperbrowser
- dotenv - For loading environment variables
- zod - For runtime type checking
