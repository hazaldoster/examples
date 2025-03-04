import fs from 'fs';
import ora from 'ora';
import HyperbrowserClient, { Hyperbrowser } from '@hyperbrowser/sdk';
import { zodResponseFormat } from "openai/helpers/zod";
import OpenAI from 'openai';

import {
  ProductResponseSchema,
  SimilarProductsResponseSchema,
  FileDataSchema,
  zodProductSchema,
  zodSimilarProductsArraySchema,
  zodSimilarProductsSchema
} from './types';
import { displayProductDetails, displaySimilarProducts } from './display';
import { z } from 'zod';

export async function searchForProduct(productUrl: string, outputFile: string, apiKey: string, openAiKey?: string) {
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
    const similarProducts = await findSimilarProducts(client, productData, openAiKey);
    spinner.succeed(`Found ${similarProducts.length} similar products${openAiKey ? ' (sorted by similarity)' : ''}`);

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

export async function refreshProductInfo(filePath: string, apiKey: string, openAiKey?: string) {
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
        const updatedSimilarProducts = await findSimilarProducts(client, productInfo.originalProduct, openAiKey);

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

async function findSimilarProducts(
  hyperbrowserClient: HyperbrowserClient,
  productData: ProductResponseSchema,
  openAiKey?: string
) {
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
    let products = similarProductsData.products;

    // Sort the products using OpenAI if API key is available
    if (openAiKey && openAiKey.trim() !== '') {
      console.log('Sorting products by similarity using OpenAI');
      products = await sortProductsBySimilarity(products, productData, openAiKey);
    } else {
      console.log('No OpenAI API key provided, skipping similarity sorting');
    }

    return products;
  } catch (error) {
    throw error; // Let the calling function handle the spinner
  }
}

async function sortProductsBySimilarity(
  products: SimilarProductsResponseSchema['products'],
  originalProduct: ProductResponseSchema,
  openAiApiKey: string
): Promise<SimilarProductsResponseSchema['products']> {
  try {
    const openai = new OpenAI({
      apiKey: openAiApiKey
    });

    // Create a prompt for OpenAI
    const prompt = `
      I have an original product and a list of similar products. Please rank the similar products by how closely they match the original product. Consider factors like features, specifications, price range, brand, and overall product purpose.
      
      Original Product:
      Name: ${originalProduct.name}
      Brand: ${originalProduct.brand}
      Description: ${originalProduct.description}
      Price: $${originalProduct.price}
      
      Similar Products:
      ${products.map((product, index) => `
      Product ${index + 1}:
      Name: ${product.name}
      Brand: ${product.brand}
      Description: ${product.description}
      Price: $${product.price}
      Sale Price: ${product.salePrice ? '$' + product.salePrice : 'N/A'}
      On Sale: ${product.onSale ? 'Yes' : 'No'}
      Link: ${product.linkToProduct}
      `).join('\n')}
      
      Return a JSON array of indices representing the ranked order of products from most similar to least similar to the original product. For example [2, 5, 1, 3, 4] would mean Product 2 is most similar, followed by Product 5, etc.
    `;

    // Call OpenAI API
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are a helpful assistant that ranks products by similarity." },
        { role: "user", content: prompt }
      ],
      response_format: zodResponseFormat(z.object({ rankedProducts: z.array(z.number()) }), "rankedProducts"),
      temperature: 0.3,
    });


    const productOrder = JSON.parse(response.choices[0]?.message?.content || '{}').rankedProducts as number[];

    // Sort the products based on the ranking order
    // Adjust indices to be 0-based (OpenAI returns 1-based indices)
    const sortedProducts = [...products];

    // Create a new array to hold the sorted products
    const reorderedProducts: typeof products = [];

    // Map each index in productOrder to the corresponding product
    // Subtract 1 from each index since productOrder uses 1-based indexing
    for (const index of productOrder) {
      // Ensure the index is valid
      if (index >= 1 && index <= products.length) {
        reorderedProducts.push(products[index - 1]);
      }
    }

    // If any products were missed in the ordering, add them at the end
    if (reorderedProducts.length < products.length) {
      const includedIndices = new Set(productOrder.map(i => i - 1));
      for (let i = 0; i < products.length; i++) {
        if (!includedIndices.has(i)) {
          reorderedProducts.push(products[i]);
        }
      }
    }

    // Replace the original products array with the sorted one
    return reorderedProducts;
  } catch (error) {
    console.error("Error sorting products with OpenAI:", error);
    // Return unsorted products if there's an error
    return products;
  }
} 