# Maps Lead Finder

This project is a command-line tool that uses HyperAgent and OpenAI's GPT-4o to find business leads from Google Maps for a specified area and business type. It returns a list of businesses with their name, address, and contact information.

## Features

- Interactive CLI for user input (area and business type)
- Uses HyperAgent and OpenAI LLM to automate Google Maps search
- Outputs a structured list of business leads

## Requirements

- Node.js (v18 or higher recommended)
- An OpenAI API key

## Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd Maps-lead-finder
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variable:

```
OPENAI_API_KEY=your_openai_api_key_here
```

You can use the provided `.env.example` as a template.

## Usage

Run the script using:

```bash
npx tsx maps-lead-finder.ts
```

Or, if you have `ts-node` installed:

```bash
npx ts-node maps-lead-finder.ts
```

You will be prompted to enter the area and business type you want to search for.

## Example

```
Enter the area to search (e.g. 'San Francisco, CA'): New York, NY
Enter the business type to find (e.g. 'restaurants'): coffee shops
```

## Output

A list of at least 5 businesses with their name, address, and contact information will be displayed.

## License

MIT
