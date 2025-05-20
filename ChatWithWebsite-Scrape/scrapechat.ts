import { Hyperbrowser } from "@hyperbrowser/sdk";
import { config } from "dotenv";
import * as readline from "readline";
import OpenAI from "openai";
import readlineSync from "readline-sync";

config();

const client = new Hyperbrowser({
  apiKey: process.env.HYPERBROWSER_API_KEY,
});
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const promptForInput = (question: string): Promise<string> => {
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
};

async function chatWithContent(content: string) {
  const messages: OpenAI.Chat.ChatCompletionMessageParam[] = [
    {
      role: "system",
      content:
        "You are a helpful assistant answering questions about the content of a webpage.",
    },
    {
      role: "user",
      content: `Here is the content of the webpage:\n\n${content}`,
    },
  ];

  console.log(
    '💬 Chat mode: Ask anything about the page (type "exit" to quit\n',
  );

  while (true) {
    const input = readlineSync.question("You: ");
    if (input.toLowerCase() === "exit") break;

    messages.push({ role: "user", content: input });

    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages,
    });

    const answer = response.choices[0].message?.content ?? "";
    console.log(`\x1b[36mAI: ${answer.trim()}\x1b[0m\n`);

    messages.push({ role: "assistant", content: answer });
  }

  console.log("👋 Chat ended.");
}

const main = async () => {
  const url = await promptForInput("Enter the URL to scrape: ");
  const scrapeResult = await client.scrape.startAndWait({ url: url });
  let scrapedContent = "";
  if (scrapeResult && scrapeResult.data) {
    if (scrapeResult.data.markdown) {
      scrapedContent = scrapeResult.data.markdown;
    } else if (scrapeResult.data.html) {
      scrapedContent = scrapeResult.data.html;
    } else {
      scrapedContent = JSON.stringify(scrapeResult.data);
    }
  }

  console.log("Scrape result received. Starting chat...\n");

  await chatWithContent(scrapedContent);
};

main();
