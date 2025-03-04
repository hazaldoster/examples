# Product Finder

A command-line tool built with TypeScript and Hyperbrowser to search for products, extract their information, find similar products, and track them over time.

## Features

- **Product Search**: Extract detailed information from any product URL
- **Similar Products**: Find similar products from Google Shopping 
- **Data Tracking**: Save product details to easily track price changes
- **Automatic Refresh**: Schedule updates to keep your product data current
- **User-Friendly Interface**: Progress indicators and clear formatted output
- **OpenAI Integration**: Use OpenAI to sort products by similarity

## Requirements

- Node.js 18 or higher
- Hyperbrowser API key (get one at [hyperbrowser.io](https://hyperbrowser.io))
- Linux/macOS for the scheduling feature (uses crontab)

## Installation

1. Clone this repository or download the source code
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the project root with your API key:
   ```
   HYPERBROWSER_API_KEY=your_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here # Optional, only needed for similarity sorting
   ```
4. Build the project:
   ```bash
   npm run build
   ```

## Usage

### Search for a Product

Extract information about a product and find similar items:

```bash
npm run search -- --url "https://example.com/product/123" --output "./my-products.json"
```

Or use the shorthand example command:

```bash
npm run search:example
```

Options:
- `--url, -u`: Product URL (required)
- `--output, -o`: Custom output file path (optional, defaults to `saved_products.json`)

### Refresh Product Data

Update the similar products for all items in your saved data:

```bash
npm run refresh -- --file "./my-products.json"
```

Or use the default file location:
```bash
npm run refresh:default
```

Options:
- `--file, -f`: Path to the saved product data file (optional, defaults to `saved_products.json`)

### Schedule Automatic Updates

Set up a cron job to run the refresh operation periodically:

```bash
npm run schedule -- --interval "0 */6 * * *" --file "./my-products.json"
```

Or use one of the preset scheduling options:
```bash
npm run schedule:daily    # Run once a day at midnight
npm run schedule:hourly   # Run every hour
npm run schedule:weekly   # Run once a week on Sunday
```

Options:
- `--interval, -i`: Cron schedule expression (optional, defaults to daily at midnight)
- `--file, -f`: Path to the saved product file (optional, defaults to `saved_products.json`)

### Remove Scheduled Updates

Remove the cron job when you no longer need automatic updates:

```bash
npm run unschedule
```

Or remove the job and delete the script file:
```bash
npm run unschedule:clean
```

Options:
- `--delete-script, -d`: Also delete the script file (optional, defaults to `false`)

## Advanced Usage

### Global Installation

You can install the tool globally to run it from anywhere:

```bash
npm install -g .
```

Then use the `product-finder` command:
```bash
product-finder search --url "https://example.com/product/123"
```

### Development Mode

For development, you can use the watch mode:

```bash
npm run dev
```

This will recompile the TypeScript code whenever you make changes.

## Data Structure

The tool stores data in JSON format with the following structure:

```json
{
  "https://example.com/product/123": {
    "originalProduct": {
      "name": "Example Product",
      "brand": "Example Brand",
      "description": "This is a great product...",
      "price": 99.99
    },
    "similarProducts": [
      {
        "name": "Similar Product 1",
        "brand": "Other Brand",
        "description": "Another great product...",
        "price": 89.99,
        "link": "https://example.com/similar1",
        "onSale": true,
        "salePrice": 79.99
      }
      // More similar products...
    ],
    "lastUpdated": "2023-11-15T12:34:56.789Z"
  }
  // More products...
}
```

## Troubleshooting

### API Key Issues
If you encounter `HYPERBROWSER_API_KEY is not set` error, make sure you:
1. Have created a `.env` file with your API key
2. Have correctly formatted the key as `HYPERBROWSER_API_KEY=your_key_here`

### Scheduling Issues
If scheduling doesn't work:
1. Ensure you're on Linux/macOS (crontab is required)
2. Check if the script has executable permissions (`chmod +x run-scheduled-task.sh`)
3. Verify your crontab entry with `crontab -l`

### Data Extraction Issues
If product information is not being extracted correctly:
1. Check if the URL is accessible
2. Verify that the product page structure matches what the extractor expects
3. Try using a proxy by setting `HYPERBROWSER_USE_PROXY=true` in your `.env` file

## License

MIT