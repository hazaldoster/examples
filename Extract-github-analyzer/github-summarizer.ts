import { Hyperbrowser } from "@hyperbrowser/sdk";
import { config } from "dotenv";
import { z } from "zod";
import * as readline from "readline";

config();

const client = new Hyperbrowser({
  apiKey: process.env.HYPERBROWSER_API_KEY,
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const promptUser = async (question: string): Promise<string> => {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
};

const main = async () => {
  const username = await promptUser("Enter a GitHub username: ");

  if (!username) {
    console.error("Username cannot be empty");
    rl.close();
    return;
  }

  const githubUrl = `https://github.com/${username}`;
  console.log(`Analyzing GitHub profile: ${githubUrl}`);

  const schema = z.object({
    username: z.string(),
    primaryLanguages: z.array(z.string()),
    frameworks: z.array(z.string()),
    tools: z.array(z.string()),
    repositories: z.array(
      z.object({
        name: z.string(),
        summary: z.string().optional(),
      }),
    ),
  });

  try {
    const result = await client.extract.startAndWait({
      urls: [githubUrl],
      prompt:
        "Summarize their tech stack, their main languages, frameworks, tools, contributions, and top repositories.",
      schema: schema,
      sessionOptions: {
        useProxy: true,
        solveCaptchas: true,
      },
    });

    console.log("Tech Stack Analysis:", JSON.stringify(result, null, 2));
  } catch (error) {
    console.error("Error analyzing GitHub profile:", error);
  } finally {
    rl.close();
  }
};

main();
