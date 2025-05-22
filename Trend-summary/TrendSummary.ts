import "dotenv/config";
import HyperAgent from "@hyperbrowser/agent";
import { Hyperbrowser } from "@hyperbrowser/sdk";
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const client = new Hyperbrowser({
  apiKey: process.env.HYPERBROWSER_API_KEY,
});

async function main() {
  const session = await client.sessions.create({
    solveCaptchas: true,
  });
  console.log("\n\n===Starting HyperAgent===\n\n");

  const agent = new HyperAgent();

  try {
    console.log("Opening first page...");
    const page1 = await agent.newPage();

    console.log("Executing first task...");
    const page1Response = await page1.ai(
     "Open Hacker News front page, find the top post published today, and extract its title, URL, and key information."
    );

    console.log(`First destination found: ${page1Response.output}`);

    console.log("Opening second page...");
    const page2 = await agent.newPage();

    console.log(`Searching for information about ${page1Response.output}... on Reddit`);
    const page2Response = await page2.ai(
     `Search Reddit for the Hacker News post title:${page1Response.output}. Find the top relevant posts and their top comments. Then, identify a recent conversation from today about the updates, and provide an overall summary of that discussion.`
    );

    console.log("\n=== Summary of Reddit discussions ===");
    console.log(page2Response.output);
  } catch (error) {
    console.error("Error during execution:", error);
  } finally {
    console.log("\nClosing agent...");
    await agent.closeAgent();
    console.log("Agent closed successfully.");
  }
}

main().catch((error) => {
  console.error("Unhandled error:", error);
});
