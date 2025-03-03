import { ProductResponseSchema, SimilarProductsResponseSchema } from './types';

// Function to display product details in console
export function displayProductDetails(product: ProductResponseSchema) {
  console.log('\n📦 Product Details:');
  console.log('='.repeat(50));
  console.log(`📌 Name: ${product.name}`);
  console.log(`🏷️ Brand: ${product.brand}`);
  console.log(`💰 Price: $${product.price.toFixed(2)}`);
  
  // Trim description if it's too long
  const maxDescLength = 150;
  const description = product.description.length > maxDescLength
    ? `${product.description.substring(0, maxDescLength)}...`
    : product.description;
  
  console.log(`📝 Description: ${description}`);
  console.log('='.repeat(50));
}

// Function to display similar products in console
export function displaySimilarProducts(products: SimilarProductsResponseSchema['products']) {
  console.log('\n🔍 Similar Products Found:');
  console.log('='.repeat(50));
  
  products.forEach((product, index) => {
    console.log(`\n#${index + 1}: ${product.name}`);
    console.log(`🏷️ Brand: ${product.brand}`);
    
    // Display price info with sale price if available
    if (product.onSale && product.salePrice !== undefined) {
      console.log(`💰 Price: $${product.price.toFixed(2)} (On Sale: $${product.salePrice.toFixed(2)})`);
    } else {
      console.log(`💰 Price: $${product.price.toFixed(2)}`);
    }
    
    // Show link shortened if needed
    const maxLinkLength = 70;
    
    console.log(`🔗 Link: ${product.linkToProduct}`);
  });
  
  console.log('='.repeat(50));
} 