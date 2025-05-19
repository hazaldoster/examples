import "dotenv/config";
import HyperAgent from "@hyperbrowser/agent";
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";
import * as readline from "readline";


async function getUserInput(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

async function main() {
  const schema = z.object({
    businesses: z.array(
      z.object({
        name: z.string(),
        address: z.string(),
        contact: z.string(),
      }),
    ),
  });

  console.log("\n===== Running Leads-Finder Agent =====");

  const llm = new ChatOpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    model: "gpt-4o",
  });

  const agent = new HyperAgent({
    llm: llm,
  });

  // Get user input for area and business type
  const area = await getUserInput(
    "Enter the area to search (e.g. 'San Francisco, CA'): ",
  );
  const businessType = await getUserInput(
    "Enter the business type to find (e.g. 'restaurants'): ",
  );

  const result = await agent.executeTask(
    `Navigate to google maps, find the businesses in the area of ${area} and ${businessType}. Return a list of at least 5 businesses with their name, address and contact information.`,
    {
      onStep: (step) => {
        console.log(`===== STEP ${step.idx} =====`);
        console.dir(step, { depth: null, colors: true });
        console.log("===============\n");
      },
      outputSchema: schema,
    },
  );
  await agent.closeAgent();
  console.log("\nResult:");
  if (
    result.output &&
    typeof result.output === "object" &&
    "businesses" in result.output
  ) {
    console.log((result.output as { businesses: any[] }).businesses);
  } else {
    console.log(result.output);
  }
  return result;
}

main().catch(console.error);
