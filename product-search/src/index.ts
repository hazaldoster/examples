import 'dotenv/config';
import path from 'path';
import { Command } from 'commander';

// Import functions from our modules
import { searchForProduct, refreshProductInfo } from './product';
import { setupCronJob, removeCronJob } from './scheduler';

// Configuration
const OUTPUT_FILE = path.join(__dirname, '../saved_products.json');
const API_KEY = process.env.HYPERBROWSER_API_KEY as string;

async function main() {
  const program = new Command();

  program
    .name('product-finder')
    .description('Tool to search for products and find similar items')
    .version('1.0.0');

  program
    .command('search')
    .description('Search for a product using a URL and find similar products')
    .requiredOption('-u, --url <url>', 'URL of the product to search')
    .option('-o, --output <file>', 'Output file path', OUTPUT_FILE)
    .action(async (options: { url: string, output: string }) => {
      if (!API_KEY) {
        throw new Error('HYPERBROWSER_API_KEY is not set');
      }
      await searchForProduct(options.url, options.output, API_KEY);
    });

  program
    .command('refresh')
    .description('Refresh information for a product using a saved file')
    .requiredOption('-f, --file <file>', 'Path to the saved product file', OUTPUT_FILE)
    .action(async (options: { file: string, }) => {
      if (!API_KEY) {
        throw new Error('HYPERBROWSER_API_KEY is not set');
      }
      await refreshProductInfo(options.file, API_KEY);
    });

  program
    .command('schedule')
    .description('Set up a cron job to run the product finder periodically')
    .option('-f, --file <file>', 'Path to the saved product file', OUTPUT_FILE)
    .option('-i, --interval <interval>', 'Cron schedule interval', '0 0 * * *') // Default: every day at midnight
    .action(async (options: { file: string, interval: string }) => {
      if (!API_KEY) {
        throw new Error('HYPERBROWSER_API_KEY is not set');
      }
      await setupCronJob(options, API_KEY);
    });

  program
    .command('unschedule')
    .description('Remove the scheduled cron job')
    .option('-d, --delete-script', 'Also delete the script file', false)
    .action(async (options: { deleteScript: boolean }) => {
      await removeCronJob(options);
    });

  await program.parseAsync(process.argv);
}

main().catch(console.error);
