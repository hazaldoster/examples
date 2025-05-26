import { Hyperbrowser } from "@hyperbrowser/sdk";
import { config } from "dotenv";
import { z } from "zod";
import readline from "readline";

config();

const client = new Hyperbrowser({
  apiKey: process.env.HYPERBROWSER_API_KEY,
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const askQuestion = (question: string): Promise<string> => {
  return new Promise((resolve) => {
    rl.question(`${colors.cyan}${question}${colors.reset}`, (answer) => {
      resolve(answer);
    });
  });
};

const colors = {
  green: "\x1b[32m",
  reset: "\x1b[0m",
  cyan: "\x1b[36m",
  yellow: "\x1b[33m",
};

const main = async () => {
  try {
    const companyName = await askQuestion("Enter the company name: ");
    const researchTopic = await askQuestion(
      "Enter what you wanna research about the company: ",
    );

    console.log(
      `${colors.cyan}Researching ${companyName} for: ${researchTopic}...${colors.reset}`,
    );

    const schema = z.object({
      companyName: z.string(),
      companyOverview: z.string(),
      researchFindings: z.string(),
      keyPoints: z.array(z.string()),
      additionalInfo: z.string().optional(),
    });

    type CompanyResearchData = z.infer<typeof schema>;

    // Search for the company and extract information
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(
      companyName + " " + researchTopic,
    )}`;

    // Use the official extract method
    const result = await client.extract.startAndWait({
      urls: [searchUrl],
      prompt: `Research and extract information about ${companyName} specifically related to: ${researchTopic}. 
      Provide:
      - Company name
      - A comprehensive overview of the company
      - Detailed findings related to the research topic: ${researchTopic}
      - Key points and insights
      - Any additional relevant information`,
      schema: schema,
    });

    // Display results in green color
    console.log(`${colors.green}`);
    console.log("=".repeat(60));
    console.log(`RESEARCH RESULTS FOR: ${companyName.toUpperCase()}`);
    console.log(`TOPIC: ${researchTopic.toUpperCase()}`);
    console.log("=".repeat(60));

    if (result.status === "completed" && result.data) {
      const data = result.data as CompanyResearchData;
      console.log(`\nCOMPANY: ${data.companyName}`);
      console.log(`\nOVERVIEW:\n${data.companyOverview}`);
      console.log(`\nRESEARCH FINDINGS:\n${data.researchFindings}`);

      if (data.keyPoints && data.keyPoints.length > 0) {
        console.log(`\nKEY POINTS:`);
        data.keyPoints.forEach((point: string, index: number) => {
          console.log(`${index + 1}. ${point}`);
        });
      }

      if (data.additionalInfo) {
        console.log(`\nADDITIONAL INFORMATION:\n${data.additionalInfo}`);
      }
    } else {
      console.log("No data found or extraction failed.");
      console.log("Result:", JSON.stringify(result, null, 2));
    }

    console.log("=".repeat(60));
    console.log(`${colors.reset}`);
  } catch (error) {
    console.error(
      `${colors.yellow}Error during research:${colors.reset}`,
      error,
    );
  } finally {
    rl.close();
  }
};

main();
