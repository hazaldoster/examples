import { Hyperbrowser } from "@hyperbrowser/sdk";
import { chromium } from "playwright-core";
import dotenv from "dotenv";
import fs from "fs";
import path from "path";

// Load environment variables
dotenv.config();

const client = new Hyperbrowser({
  apiKey: process.env.HYPERBROWSER_API_KEY,
});

const main = async () => {
  let session = null;
  let browser = null;
  try {
    console.log("📖 TWEET VIEWER: Extracting tweet content...");
    console.log("📱 Target: https://x.com/OguzhanUgur");
    
    // Create a session for browser automation
    console.log("🔧 Creating browser session...");
    session = await client.sessions.create({
      useStealth: true,
      acceptCookies: false,
    });
    
    console.log("🌐 Connecting to browser...");
    browser = await chromium.connectOverCDP(session.wsEndpoint);
    const defaultContext = browser.contexts()[0];
    const page = await defaultContext.newPage();
    
    console.log("📱 Navigating to Twitter profile...");
    await page.goto("https://x.com/OguzhanUgur", { waitUntil: "networkidle" });
    
    // Wait for page to load
    await page.waitForTimeout(3000);
    
    console.log("📜 Extracting tweet content...");
    
    // Extract tweet data
    const tweets = await page.evaluate(() => {
      const tweetElements = document.querySelectorAll('[data-testid="tweet"]');
      const tweetData = [];
      
      tweetElements.forEach((tweet, index) => {
        try {
          // Tweet text
          const tweetTextElement = tweet.querySelector('[data-testid="tweetText"]');
          const tweetText = tweetTextElement ? tweetTextElement.innerText : 'No text found';
          
          // Author name
          const authorElement = tweet.querySelector('[data-testid="User-Name"]');
          const author = authorElement ? authorElement.innerText : 'Unknown author';
          
          // Time
          const timeElement = tweet.querySelector('time');
          const time = timeElement ? timeElement.getAttribute('datetime') : 'Unknown time';
          
          // Engagement stats
          const replyElement = tweet.querySelector('[data-testid="reply"]');
          const retweetElement = tweet.querySelector('[data-testid="retweet"]');
          const likeElement = tweet.querySelector('[data-testid="like"]');
          
          const replies = replyElement ? replyElement.getAttribute('aria-label') || '0' : '0';
          const retweets = retweetElement ? retweetElement.getAttribute('aria-label') || '0' : '0';
          const likes = likeElement ? likeElement.getAttribute('aria-label') || '0' : '0';
          
          tweetData.push({
            index: index + 1,
            author: author.split('\n')[0], // Get just the name part
            text: tweetText,
            time: time,
            engagement: {
              replies,
              retweets,
              likes
            }
          });
        } catch (error) {
          console.log(`Error processing tweet ${index + 1}:`, error.message);
        }
      });
      
      return tweetData;
    });
    
    console.log(`✅ Extracted ${tweets.length} tweets!`);
    
    // Save tweets to JSON
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputDir = 'output';
    
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const tweetsFile = path.join(outputDir, `extracted_tweets_${timestamp}.json`);
    fs.writeFileSync(tweetsFile, JSON.stringify(tweets, null, 2));
    console.log(`💾 Tweets saved to: ${tweetsFile}`);
    
    // Display tweets in console
    console.log("\n" + "=".repeat(80));
    console.log("📱 TWEETS FROM @OguzhanUgur");
    console.log("=".repeat(80));
    
    tweets.forEach((tweet, index) => {
      console.log(`\n📝 Tweet #${tweet.index}`);
      console.log(`👤 Author: ${tweet.author}`);
      console.log(`⏰ Time: ${new Date(tweet.time).toLocaleString()}`);
      console.log(`💬 Text: ${tweet.text}`);
      console.log(`📊 Engagement: ${tweet.engagement.likes} likes, ${tweet.engagement.retweets} retweets, ${tweet.engagement.replies} replies`);
      console.log("-".repeat(60));
    });
    
    console.log(`\n🎉 Total: ${tweets.length} tweets displayed`);
    
    // Close browser
    if (browser) {
      await browser.close();
    }
    
  } catch (error) {
    console.error("❌ Error:", error.message);
    process.exit(1);
  } finally {
    if (session) {
      try {
        await client.sessions.stop(session.id);
      } catch (cleanupError) {
        console.warn("⚠️ Warning: Could not stop session:", cleanupError.message);
      }
    }
  }
};

if (!process.env.HYPERBROWSER_API_KEY) {
  console.error("❌ HYPERBROWSER_API_KEY environment variable is required!");
  process.exit(1);
}

main().catch((error) => {
  console.error("💥 Unhandled error:", error.message);
  process.exit(1);
}); 