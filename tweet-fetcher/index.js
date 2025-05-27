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
    console.log("🚀 Starting Twitter scraping process...");
    console.log("📱 Target: https://x.com/OguzhanUgur");
    console.log("🎯 Goal: Fetch first 1000 tweets");
    
    // Create a session for browser automation
    console.log("🔧 Creating browser session...");
    session = await client.sessions.create({
      useStealth: true,  // Twitter için önerilir
      // useProxy: true,    // Premium plan gerekli
      // solveCaptchas: true, // Premium plan gerekli
      acceptCookies: false,
    });
    
    console.log("🌐 Connecting to browser...");
    browser = await chromium.connectOverCDP(session.wsEndpoint);
    const defaultContext = browser.contexts()[0];
    const page = await defaultContext.newPage();
    
    console.log("📱 Navigating to Twitter profile...");
    await page.goto("https://x.com/OguzhanUgur", { waitUntil: "networkidle" });
    
    // Wait for initial page load
    console.log("⏳ Waiting for page to load...");
    await page.waitForTimeout(3000);
    
    let tweetCount = 0;
    let scrollCount = 0;
    const maxScrolls = 100; // Hedef: ~1000 tweet
    const scrollDelay = 1500; // Her scroll arası bekleme
    
    console.log("📜 Starting scroll process to collect tweets...");
    
    while (scrollCount < maxScrolls) {
      // Count current tweets on page
      const currentTweets = await page.locator('[data-testid="tweet"]').count();
      
      if (currentTweets > tweetCount) {
        tweetCount = currentTweets;
        console.log(`📊 Tweets collected so far: ${tweetCount} (Scroll ${scrollCount + 1}/${maxScrolls})`);
      }
      
      // Scroll to bottom of page
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });
      
      // Wait for new content to load
      await page.waitForTimeout(scrollDelay);
      
      scrollCount++;
      
      // Check if we've reached a reasonable tweet count or if no new tweets are loading
      if (tweetCount >= 1000) {
        console.log(`🎯 Target reached! Collected ${tweetCount} tweets`);
        break;
      }
      
      // Check if page has stopped loading new content
      if (scrollCount > 10 && scrollCount % 10 === 0) {
        const newTweetCount = await page.locator('[data-testid="tweet"]').count();
        if (newTweetCount === tweetCount) {
          console.log("⚠️ No new tweets loading, may have reached end of timeline");
          break;
        }
      }
    }
    
    console.log("📸 Taking final screenshot...");
    const screenshot = await page.screenshot({ fullPage: true });
    
    console.log("📝 Extracting page content...");
    const htmlContent = await page.content();
    
    // Get page title and other metadata
    const title = await page.title();
    const url = page.url();
    
    // Create markdown from the page
    const markdownContent = `# ${title}\n\nURL: ${url}\nTweets Collected: ${tweetCount}\nScrolls Performed: ${scrollCount}\nTimestamp: ${new Date().toISOString()}\n\n## Content\n\n[Full HTML content extracted]`;
    
    // Simulate the scrape result structure
    const scrapeResult = {
      data: {
        markdown: markdownContent,
        html: htmlContent,
        screenshot: `data:image/png;base64,${screenshot.toString('base64')}`,
        metadata: {
          title,
          url,
          tweetCount,
          scrollCount,
          timestamp: new Date().toISOString()
        }
      }
    };

    console.log("✅ Scraping completed successfully!");
    
    // Sonuçları kaydet
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputDir = 'output';
    
    // Output klasörü oluştur
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Markdown formatını kaydet
    if (scrapeResult.data.markdown) {
      const markdownFile = path.join(outputDir, `tweets_${timestamp}.md`);
      fs.writeFileSync(markdownFile, scrapeResult.data.markdown);
      console.log(`📝 Markdown saved to: ${markdownFile}`);
    }
    
    // HTML formatını kaydet
    if (scrapeResult.data.html) {
      const htmlFile = path.join(outputDir, `tweets_${timestamp}.html`);
      fs.writeFileSync(htmlFile, scrapeResult.data.html);
      console.log(`🌐 HTML saved to: ${htmlFile}`);
    }
    
    // Links formatını kaydet
    if (scrapeResult.data.links) {
      const linksFile = path.join(outputDir, `links_${timestamp}.json`);
      fs.writeFileSync(linksFile, JSON.stringify(scrapeResult.data.links, null, 2));
      console.log(`🔗 Links saved to: ${linksFile}`);
    }
    
    // Screenshot'ı kaydet
    if (scrapeResult.data.screenshot) {
      const screenshotFile = path.join(outputDir, `screenshot_${timestamp}.png`);
      // Base64 string'i binary'ye çevir ve kaydet
      const base64Data = scrapeResult.data.screenshot.replace(/^data:image\/\w+;base64,/, "");
      fs.writeFileSync(screenshotFile, base64Data, 'base64');
      console.log(`📸 Screenshot saved to: ${screenshotFile}`);
    }
    
    // Metadata kaydet
    const metadata = {
      url: "https://x.com/OguzhanUgur",
      timestamp: new Date().toISOString(),
      totalScrolls: scrapeResult.metadata?.scrollCount || "unknown",
      sessionOptions: scrapeResult.metadata?.sessionOptions || {},
      processingTime: scrapeResult.metadata?.processingTime || "unknown"
    };
    
    const metadataFile = path.join(outputDir, `metadata_${timestamp}.json`);
    fs.writeFileSync(metadataFile, JSON.stringify(metadata, null, 2));
    console.log(`📊 Metadata saved to: ${metadataFile}`);
    
    // Temel istatistikleri göster
    console.log("\n📈 Scraping Statistics:");
    console.log(`⏱️  Processing completed at: ${new Date().toLocaleString()}`);
    
    if (scrapeResult.data.markdown) {
      const tweetCount = (scrapeResult.data.markdown.match(/\n[\s]*\d+[.]/g) || []).length;
      console.log(`🐦 Estimated tweets scraped: ${tweetCount}`);
    }
    
    console.log(`💾 Files saved in: ./${outputDir}/`);
    
    // Close browser and clean up
    if (browser) {
      await browser.close();
      console.log("🔒 Browser closed");
    }
    
  } catch (error) {
    console.error("❌ Error during scraping:", error.message);
    
    // Hata detaylarını kaydet
    const errorLog = {
      timestamp: new Date().toISOString(),
      error: error.message,
      stack: error.stack,
      url: "https://x.com/OguzhanUgur"
    };
    
    if (!fs.existsSync('output')) {
      fs.mkdirSync('output', { recursive: true });
    }
    
    const errorFile = path.join('output', `error_${new Date().toISOString().replace(/[:.]/g, '-')}.json`);
    fs.writeFileSync(errorFile, JSON.stringify(errorLog, null, 2));
    console.log(`🚨 Error log saved to: ${errorFile}`);
    
    process.exit(1);
  } finally {
    // Clean up session
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

// API anahtarını kontrol et
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