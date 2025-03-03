import z from 'zod';

// Product schemas
export const zodProductSchema = z.object({
  name: z.string(),
  brand: z.string(),
  description: z.string(),
  price: z.number()
});

export const zodSimilarProductsSchema = zodProductSchema.extend({
  link: z.string(),
  onSale: z.boolean(),
  salePrice: z.number().optional()
});

export const zodSimilarProductsArraySchema = z.object({ 
  products: z.array(zodSimilarProductsSchema) 
});

// Type definitions
export type ProductResponseSchema = z.infer<typeof zodProductSchema>;
export type SimilarProductsResponseSchema = z.infer<typeof zodSimilarProductsArraySchema>;

export type FileDataSchema = {
  [key: string]: {
    originalProduct: ProductResponseSchema;
    similarProducts: SimilarProductsResponseSchema['products'];
    lastUpdated: string;
  };
}; 