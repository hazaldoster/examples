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
    console.log("🚀 TWEET COLLECTOR: Collecting 100 tweets...");
    console.log("📱 Target: https://x.com/OguzhanUgur");
    console.log("🎯 Goal: Collect exactly 100 tweets");
    
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
    
    // Wait for initial page load
    await page.waitForTimeout(5000);
    
    let allTweets = [];
    let scrollCount = 0;
    const maxScrolls = 50; // Increased scroll limit
    const scrollDelay = 2000; // Slower for better loading
    const targetTweetCount = 100;
    
    console.log("📜 Starting tweet collection process...");
    console.log("🔄 Will scroll and collect tweets in batches...");
    
    while (scrollCount < maxScrolls && allTweets.length < targetTweetCount) {
      // Extract current tweets on page
      console.log(`\n🔍 Extracting tweets... (Scroll ${scrollCount + 1}/${maxScrolls})`);
      
      const currentBatch = await page.evaluate(() => {
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
            
            // Tweet URL/ID (for deduplication)
            const linkElement = tweet.querySelector('a[href*="/status/"]');
            const tweetUrl = linkElement ? linkElement.href : null;
            const tweetId = tweetUrl ? tweetUrl.split('/status/')[1]?.split('?')[0] : `temp_${index}_${Date.now()}`;
            
            // Engagement stats
            const replyElement = tweet.querySelector('[data-testid="reply"]');
            const retweetElement = tweet.querySelector('[data-testid="retweet"]');
            const likeElement = tweet.querySelector('[data-testid="like"]');
            
            const replies = replyElement ? replyElement.getAttribute('aria-label') || '0' : '0';
            const retweets = retweetElement ? retweetElement.getAttribute('aria-label') || '0' : '0';
            const likes = likeElement ? likeElement.getAttribute('aria-label') || '0' : '0';
            
            // Check if it's a valid tweet (has text and author)
            if (tweetText !== 'No text found' && author !== 'Unknown author') {
              tweetData.push({
                id: tweetId,
                author: author.split('\n')[0], // Get just the name part
                text: tweetText,
                time: time,
                url: tweetUrl,
                engagement: {
                  replies: replies.replace(/[^\d]/g, '') || '0',
                  retweets: retweets.replace(/[^\d]/g, '') || '0',
                  likes: likes.replace(/[^\d]/g, '') || '0'
                },
                extractedAt: new Date().toISOString()
              });
            }
          } catch (error) {
            console.log(`Error processing tweet ${index + 1}:`, error.message);
          }
        });
        
        return tweetData;
      });
      
      // Deduplicate tweets by ID
      const newTweets = currentBatch.filter(tweet => 
        !allTweets.some(existing => existing.id === tweet.id)
      );
      
      allTweets.push(...newTweets);
      
      console.log(`📊 Batch ${scrollCount + 1}: Found ${currentBatch.length} tweets, ${newTweets.length} new`);
      console.log(`📈 Total unique tweets collected: ${allTweets.length}/${targetTweetCount}`);
      
      // Save progress every 10 scrolls
      if ((scrollCount + 1) % 10 === 0) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const progressFile = path.join('output', `progress_${allTweets.length}_tweets_${timestamp}.json`);
        fs.writeFileSync(progressFile, JSON.stringify(allTweets, null, 2));
        console.log(`💾 Progress saved: ${progressFile}`);
      }
      
      // Check if we've reached our target
      if (allTweets.length >= targetTweetCount) {
        console.log(`🎯 Target reached! Collected ${allTweets.length} tweets`);
        break;
      }
      
      // Scroll to load more tweets
      console.log("📜 Scrolling to load more tweets...");
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });
      
      // Wait for new content to load
      await page.waitForTimeout(scrollDelay);
      
      scrollCount++;
      
      // Check if no new tweets are loading (reached end)
      if (scrollCount > 10 && newTweets.length === 0) {
        console.log("⚠️ No new tweets loading, may have reached end of timeline");
        // Try scrolling a bit more
        for (let i = 0; i < 3; i++) {
          await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
          await page.waitForTimeout(3000);
        }
        
        // Check one more time
        const finalCheck = await page.evaluate(() => 
          document.querySelectorAll('[data-testid="tweet"]').length
        );
        
        if (finalCheck === currentBatch.length) {
          console.log("🔚 Confirmed: No more tweets available");
          break;
        }
      }
    }
    
    // Final processing and save
    console.log("\n✅ Collection completed!");
    console.log(`📊 Final count: ${allTweets.length} tweets`);
    
    // Take final screenshot
    console.log("📸 Taking final screenshot...");
    const screenshot = await page.screenshot({ fullPage: false });
    
    // Save final results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputDir = 'output';
    
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Save tweets JSON
    const tweetsFile = path.join(outputDir, `100_tweets_${timestamp}.json`);
    fs.writeFileSync(tweetsFile, JSON.stringify(allTweets, null, 2));
    console.log(`💾 All tweets saved to: ${tweetsFile}`);
    
    // Save human-readable format
    const readableFile = path.join(outputDir, `100_tweets_readable_${timestamp}.txt`);
    let readableContent = `TWEETS FROM @OguzhanUgur\n`;
    readableContent += `Collected: ${allTweets.length} tweets\n`;
    readableContent += `Date: ${new Date().toLocaleString()}\n`;
    readableContent += "=".repeat(80) + "\n\n";
    
    allTweets.forEach((tweet, index) => {
      readableContent += `TWEET #${index + 1}\n`;
      readableContent += `Author: ${tweet.author}\n`;
      readableContent += `Time: ${new Date(tweet.time).toLocaleString()}\n`;
      readableContent += `Text: ${tweet.text}\n`;
      readableContent += `Engagement: ${tweet.engagement.likes} likes, ${tweet.engagement.retweets} retweets, ${tweet.engagement.replies} replies\n`;
      readableContent += `URL: ${tweet.url || 'N/A'}\n`;
      readableContent += "-".repeat(60) + "\n\n";
    });
    
    fs.writeFileSync(readableFile, readableContent);
    console.log(`📝 Readable format saved to: ${readableFile}`);
    
    // Save screenshot
    const screenshotFile = path.join(outputDir, `100_tweets_screenshot_${timestamp}.png`);
    fs.writeFileSync(screenshotFile, screenshot);
    console.log(`📸 Screenshot saved to: ${screenshotFile}`);
    
    // Save metadata
    const metadata = {
      totalTweets: allTweets.length,
      targetTweets: targetTweetCount,
      scrollsPerformed: scrollCount,
      url: "https://x.com/OguzhanUgur",
      timestamp: new Date().toISOString(),
      oldestTweet: allTweets.length > 0 ? allTweets[allTweets.length - 1].time : null,
      newestTweet: allTweets.length > 0 ? allTweets[0].time : null,
      uniqueAuthors: [...new Set(allTweets.map(t => t.author))],
      averageEngagement: {
        likes: Math.round(allTweets.reduce((sum, t) => sum + parseInt(t.engagement.likes || 0), 0) / allTweets.length),
        retweets: Math.round(allTweets.reduce((sum, t) => sum + parseInt(t.engagement.retweets || 0), 0) / allTweets.length),
        replies: Math.round(allTweets.reduce((sum, t) => sum + parseInt(t.engagement.replies || 0), 0) / allTweets.length)
      }
    };
    
    const metadataFile = path.join(outputDir, `100_tweets_metadata_${timestamp}.json`);
    fs.writeFileSync(metadataFile, JSON.stringify(metadata, null, 2));
    console.log(`📊 Metadata saved to: ${metadataFile}`);
    
    // Display summary
    console.log("\n" + "=".repeat(80));
    console.log("🎉 COLLECTION SUMMARY");
    console.log("=".repeat(80));
    console.log(`📊 Total tweets collected: ${allTweets.length}`);
    console.log(`🎯 Target achievement: ${Math.round((allTweets.length / targetTweetCount) * 100)}%`);
    console.log(`📜 Scrolls performed: ${scrollCount}`);
    console.log(`⏱️  Collection time: ${new Date().toLocaleString()}`);
    console.log(`📁 Files saved in: ./${outputDir}/`);
    
    if (allTweets.length > 0) {
      console.log(`📅 Date range: ${new Date(allTweets[allTweets.length - 1].time).toLocaleDateString()} to ${new Date(allTweets[0].time).toLocaleDateString()}`);
      console.log(`👤 Authors found: ${metadata.uniqueAuthors.length}`);
      console.log(`💖 Average engagement: ${metadata.averageEngagement.likes} likes`);
    }
    
    // Close browser
    if (browser) {
      await browser.close();
      console.log("🔒 Browser closed");
    }
    
  } catch (error) {
    console.error("❌ Error during collection:", error.message);
    
    // Save error log
    const errorLog = {
      timestamp: new Date().toISOString(),
      error: error.message,
      stack: error.stack,
      url: "https://x.com/OguzhanUgur",
      tweetsCollectedSoFar: allTweets ? allTweets.length : 0
    };
    
    if (!fs.existsSync('output')) {
      fs.mkdirSync('output', { recursive: true });
    }
    
    const errorFile = path.join('output', `error_100tweets_${new Date().toISOString().replace(/[:.]/g, '-')}.json`);
    fs.writeFileSync(errorFile, JSON.stringify(errorLog, null, 2));
    console.log(`🚨 Error log saved to: ${errorFile}`);
    
    process.exit(1);
  } finally {
    if (session) {
      try {
        await client.sessions.stop(session.id);
        console.log("🛑 Session stopped successfully");
      } catch (cleanupError) {
        console.warn("⚠️ Warning: Could not stop session:", cleanupError.message);
      }
    }
  }
};

if (!process.env.HYPERBROWSER_API_KEY) {
  console.error("❌ HYPERBROWSER_API_KEY environment variable is required!");
  console.log("💡 Please create a .env file with your API key:");
  console.log("   HYPERBROWSER_API_KEY=your_api_key_here");
  console.log("🔑 Get your API key from: https://app.hyperbrowser.ai");
  process.exit(1);
}

main().catch((error) => {
  console.error("💥 Unhandled error:", error.message);
  process.exit(1);
}); 