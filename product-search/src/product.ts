import fs from 'fs';
import ora from 'ora';
import HyperbrowserClient, { Hyperbrowser } from '@hyperbrowser/sdk';

import {
  ProductResponseSchema,
  SimilarProductsResponseSchema,
  FileDataSchema,
  zodProductSchema,
  zodSimilarProductsArraySchema
} from './types';
import { displayProductDetails, displaySimilarProducts } from './display';

export async function searchForProduct(productUrl: string, outputFile: string, apiKey: string) {
  // Create a single spinner instance to reuse
  const spinner = ora('Initializing Hyperbrowser...').start();

  let client;
  try {
    client = new Hyperbrowser({
      apiKey: apiKey
    });
    spinner.succeed('Browser initialized');

    // Extract product data
    spinner.start(`Extracting product information from ${productUrl}`);
    const productData = await extractProductData(client, productUrl);

    if (!productData) {
      spinner.fail('Failed to extract product data');
      return;
    }
    spinner.succeed(`Product found: ${productData.name}`);

    // Display detailed product information
    displayProductDetails(productData);

    // Find similar products
    spinner.start(`Finding similar products for ${productData.name}`);
    const similarProducts = await findSimilarProducts(client, productData);
    spinner.succeed(`Found ${similarProducts.length} similar products`);

    // Display similar products information
    displaySimilarProducts(similarProducts);

    // Prepare the results
    const results = {
      originalProduct: productData,
      similarProducts: similarProducts,
      lastUpdated: new Date().toISOString()
    };

    // Check if the file exists and is not empty
    spinner.start(`Saving results to ${outputFile}`);
    let existingData: FileDataSchema = {};
    if (fs.existsSync(outputFile) && fs.statSync(outputFile).size > 0) {
      try {
        const fileContent = fs.readFileSync(outputFile, 'utf8');
        existingData = JSON.parse(fileContent);
        spinner.text = `Existing data found in ${outputFile}, updating...`;
      } catch (err) {
        spinner.warn(`Error reading existing file: ${err}, creating new file instead`);
      }
    }

    // Merge with existing data or create new file
    const updatedResults = { ...existingData, [productUrl]: results };
    fs.writeFileSync(outputFile, JSON.stringify(updatedResults, null, 2));
    spinner.succeed(`Results saved to ${outputFile}`);
  } catch (error) {
    spinner.fail('Error during product search');
    console.error('Error details:', error);
  }
}

export async function refreshProductInfo(filePath: string, apiKey: string) {
  // Create a single spinner instance to reuse
  const spinner = ora(`Reading product information from ${filePath}`).start();

  let existingData: FileDataSchema;

  try {
    // 1. Read the product data from the file
    if (!fs.existsSync(filePath)) {
      spinner.fail(`File not found: ${filePath}`);
      return;
    }

    const fileContent = fs.readFileSync(filePath, 'utf8');
    existingData = JSON.parse(fileContent);

    if (Object.keys(existingData).length === 0) {
      spinner.fail(`No products found in file: ${filePath}`);
      return;
    }

    spinner.succeed(`Found ${Object.keys(existingData).length} products to refresh`);

    // Initialize the browser client
    spinner.start('Initializing Hyperbrowser...');
    let client;
    try {
      client = new Hyperbrowser({
        apiKey: apiKey
      });
      spinner.succeed('Browser initialized');
    } catch (error) {
      spinner.fail('Failed to initialize browser');
      console.error('Error:', error);
      return;
    }

    // 2 & 3. Iterate through each product URL and refresh its data
    const updatedData: FileDataSchema = {};
    let successCount = 0;
    let failCount = 0;

    for (const [productUrl, productInfo] of Object.entries(existingData)) {
      spinner.start(`Refreshing product information for: ${productUrl}`);

      // Display original product information
      console.log('\n📦 Refreshing product:');
      displayProductDetails(productInfo.originalProduct);

      try {
        // Find updated similar products
        const updatedSimilarProducts = await findSimilarProducts(client, productInfo.originalProduct);

        // Update the entry
        updatedData[productUrl] = {
          originalProduct: productInfo.originalProduct,
          similarProducts: updatedSimilarProducts,
          lastUpdated: new Date().toISOString()
        };

        spinner.succeed(`Successfully refreshed data for ${productUrl}`);

        // Display updated similar products
        displaySimilarProducts(updatedSimilarProducts);

        successCount++;
      } catch (error) {
        spinner.fail(`Error refreshing data for ${productUrl}`);
        console.error('Error details:', error);
        // Keep the existing data if refresh fails
        updatedData[productUrl] = productInfo;
        failCount++;
      }
    }

    // 4. Save the updated results back to the file
    spinner.start(`Saving refreshed data to ${filePath}`);
    fs.writeFileSync(filePath, JSON.stringify(updatedData, null, 2));
    spinner.succeed(`Refreshed data saved to ${filePath} (${successCount} success, ${failCount} failed)`);

  } catch (error) {
    spinner.fail('Error during product refresh');
    console.error('Error details:', error);
  }
}

async function extractProductData(hyperbrowserClient: HyperbrowserClient, productUrl: string): Promise<ProductResponseSchema | undefined> {
  try {
    // No spinner here because we're using one in the calling function
    const productDataResponse = await hyperbrowserClient.extract.startAndWait({
      urls: [productUrl],
      schema: zodProductSchema,
      sessionOptions: {
        useProxy: true,
        solveCaptchas: true,
      }
    });

    if (productDataResponse.error) {
      throw new Error(productDataResponse.error);
    }

    const productData = productDataResponse.data as ProductResponseSchema;
    return productData;
  } catch (error) {
    throw error; // Let the calling function handle the spinner
  }
}

async function findSimilarProducts(hyperbrowserClient: HyperbrowserClient, productData: ProductResponseSchema) {
  try {
    // No spinner here because we're using one in the calling function
    const searchQuery = `${productData.name} similar products`;
    const encodedQuery = encodeURIComponent(searchQuery);
    const googleUrl = `https://www.bing.com/shop?q=${encodedQuery}`;

    const similarProducts = await hyperbrowserClient.extract.startAndWait({
      urls: [googleUrl],
      schema: zodSimilarProductsArraySchema,
      prompt: "Extract the details on the products listed on the page. Get the name, description, brand, price, product link, sales price, and if the product is on sale for each of the products.",
      sessionOptions: {
        useProxy: true,
        solveCaptchas: true,
      }
    });

    if (similarProducts.error) {
      throw new Error(similarProducts.error);
    }

    const similarProductsData = similarProducts.data as SimilarProductsResponseSchema;
    return similarProductsData.products;
  } catch (error) {
    throw error; // Let the calling function handle the spinner
  }
} 