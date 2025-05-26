# Company Researcher

An intelligent company research tool that uses AI-powered web extraction to gather comprehensive information about any company based on your specific research topics.

## Features

- 🔍 **Smart Company Research**: Enter any company name and research topic to get detailed insights
- 🤖 **AI-Powered Extraction**: Uses HyperBrowser's advanced extraction capabilities to gather structured data
- 📊 **Structured Output**: Returns organized information including company overview, research findings, and key points
- 🎨 **Interactive CLI**: Beautiful command-line interface with colored output
- ⚡ **Fast & Reliable**: Leverages Google search and AI extraction for accurate results

## What It Does

This tool allows you to research any company on any topic by:

1. Taking a company name and research topic as input
2. Performing intelligent web searches
3. Extracting and structuring relevant information using AI
4. Presenting the findings in a clear, organized format

Perfect for:

- Market research
- Competitive analysis
- Due diligence
- Investment research
- Business intelligence

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- HyperBrowser API key

## Setup

### 1. Get Your HyperBrowser API Key

Get your HyperBrowser API key at **[hyperbrowser.ai](https://hyperbrowser.ai)**

### 2. Clone and Install

```bash
# Navigate to the project directory
cd company-researcher

# Install dependencies
npm install
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
HYPERBROWSER_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual HyperBrowser API key from [hyperbrowser.ai](https://hyperbrowser.ai).

## Usage

### Running the Application

```bash
npx ts-node company-researcher.ts
```

### Interactive Process

1. **Enter Company Name**: Type the name of the company you want to research
2. **Enter Research Topic**: Specify what aspect you want to research (e.g., "financial performance", "recent news", "market position", "sustainability initiatives")
3. **View Results**: The tool will display structured research findings

### Example Session

```
Enter the company name: Tesla
Enter what you wanna research about the company: recent innovations

Researching Tesla for: recent innovations...

============================================================
RESEARCH RESULTS FOR: TESLA
TOPIC: RECENT INNOVATIONS
============================================================

COMPANY: Tesla, Inc.

OVERVIEW:
Tesla, Inc. is an American multinational automotive and clean energy company...

RESEARCH FINDINGS:
Recent innovations from Tesla include advancements in battery technology...

KEY POINTS:
1. Introduction of 4680 battery cells with improved energy density
2. Full Self-Driving (FSD) Beta expansion
3. Supercharger network expansion globally
...

============================================================
```

## Output Structure

The tool provides structured output including:

- **Company Name**: Verified company name
- **Company Overview**: General information about the company
- **Research Findings**: Specific information related to your research topic
- **Key Points**: Bullet-pointed insights and highlights
- **Additional Information**: Supplementary relevant details

## Dependencies

- **@hyperbrowser/sdk**: HyperBrowser SDK for AI-powered web extraction
- **dotenv**: Environment variable management
- **zod**: Schema validation for structured data
- **readline**: Interactive command-line interface
- **TypeScript**: Type-safe development

## Development

### Project Structure

```
company-researcher/
├── company-researcher.ts    # Main application file
├── package.json            # Project dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

### TypeScript Configuration

The project uses TypeScript with strict type checking. The main logic is in `company-researcher.ts` which:

1. Sets up the HyperBrowser client
2. Creates an interactive CLI interface
3. Processes user input
4. Performs AI-powered web extraction
5. Displays formatted results

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your HyperBrowser API key is correctly set in the `.env` file
2. **Network Issues**: Ensure you have a stable internet connection for web searches
3. **TypeScript Errors**: Run `npm install` to ensure all dependencies are installed

### Getting Help

- Check the [HyperBrowser documentation](https://hyperbrowser.ai) for API-related issues
- Ensure your API key has sufficient credits
- Verify that the company name is spelled correctly

## License

ISC

## Contributing

Feel free to submit issues and enhancement requests!

---

**Note**: This tool requires a valid HyperBrowser API key. Get yours at [hyperbrowser.ai](https://hyperbrowser.ai) to start researching companies with AI-powered intelligence.
