import { config } from "dotenv";
import { Hyperbrowser } from "@hyperbrowser/sdk";
import * as readline from "readline";
import { z } from "zod";

config();

const hbClient = new Hyperbrowser({
  apiKey: process.env.HYPERBROWSER_API_KEY,
});

function promptForUrl(): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question("Enter the URL to validate: ", (url) => {
      rl.close();
      resolve(url.trim());
    });
  });
}

async function main() {
  const AnalysisSchema = z.array(z.string());
  const SuggestionsSchema = z.array(z.string());
  console.log("Starting CTA Validator Agent...");
  const targetUrl = process.argv[2] || (await promptForUrl());

  if (!targetUrl) {
    console.error("No URL provided. Exiting.");
    return;
  }

  console.log(`Validating CTA buttons on: ${targetUrl}`);
  const session = await hbClient.sessions.create();

  try {
    //Identify the CTA button
    console.log("Step 1: Identifying CTA button in hero section...");
    const result = await hbClient.agents.cua.startAndWait({
      task: `Navigate to ${targetUrl} and identify the main call-to-action button within the hero section at the top of the page. Ignore any CTAs in other sections.`,
      sessionId: session.id,
      keepBrowserOpen: true,
      maxSteps: 20,
    });

    const validationResults = result.data?.finalResult;
    console.log(`Output:\n${validationResults}`);

    if (!validationResults) {
      console.log("Could not identify the CTA button.");
      return;
    }

    // Analyze the CTA
    console.log("Step 2: Analyzing CTA for accessibility and SEO...");
    const analysis = await hbClient.agents.cua.startAndWait({
      task: `Analyze the CTA button you identified in the hero section for accessibility and SEO best practices. Check color contrast, text clarity, and positioning. The CTA button identified was: ${validationResults}`,

      sessionId: session.id,
      keepBrowserOpen: true,
      maxSteps: 15,
    });
    console.log(`\nAnalysis:\n${analysis.data?.finalResult}`);

    // Get improvement suggestions
    console.log("Step 3: Generating improvement suggestions...");
    const suggestions = await hbClient.agents.cua.startAndWait({
      task: `Based on your analysis of the hero section CTA button, provide 3-5 specific suggestions to improve it. Here was the previous analysis: ${analysis.data?.finalResult}`,
      sessionId: session.id,
      maxSteps: 15,
    });

    // Add more detailed logging to debug
    console.log("Raw suggestions response:", JSON.stringify(suggestions.data));
    console.log(`\nSuggestions:\n${suggestions.data?.finalResult}`);
  } catch (err) {
    console.error(`Error: ${err}`);
  } finally {
    await hbClient.sessions.stop(session.id);
  }
}

main().catch((err) => {
  console.error(`Error: ${err.message}`);
});
