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
    console.log("🚀 DEMO: Starting Twitter scraping process...");
    console.log("📱 Target: https://x.com/OguzhanUgur");
    console.log("🎯 Goal: Demo with 5 scrolls only");
    
    // Create a session for browser automation
    console.log("🔧 Creating browser session...");
    session = await client.sessions.create({
      useStealth: true,  // Twitter için önerilir
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
    const maxScrolls = 5; // Demo: sadece 5 scroll
    const scrollDelay = 1000; // Demo: daha hızlı
    
    console.log("📜 Starting DEMO scroll process...");
    
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
    }
    
    console.log("📸 Taking final screenshot...");
    const screenshot = await page.screenshot({ fullPage: false }); // Sadece görünür alan
    
    console.log("✅ DEMO completed successfully!");
    
    // Sonuçları kaydet
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputDir = 'output';
    
    // Output klasörü oluştur
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Screenshot'ı kaydet
    const screenshotFile = path.join(outputDir, `demo_screenshot_${timestamp}.png`);
    fs.writeFileSync(screenshotFile, screenshot);
    console.log(`📸 Demo screenshot saved to: ${screenshotFile}`);
    
    // Metadata kaydet
    const metadata = {
      mode: "DEMO",
      url: "https://x.com/OguzhanUgur",
      timestamp: new Date().toISOString(),
      totalScrolls: scrollCount,
      tweetCount: tweetCount,
      maxScrolls: maxScrolls
    };
    
    const metadataFile = path.join(outputDir, `demo_metadata_${timestamp}.json`);
    fs.writeFileSync(metadataFile, JSON.stringify(metadata, null, 2));
    console.log(`📊 Demo metadata saved to: ${metadataFile}`);
    
    console.log("\n🎉 DEMO Results:");
    console.log(`🐦 Tweets found: ${tweetCount}`);
    console.log(`📜 Scrolls completed: ${scrollCount}/${maxScrolls}`);
    console.log(`⏱️  Completed at: ${new Date().toLocaleString()}`);
    console.log(`💾 Files saved in: ./${outputDir}/`);
    
    // Close browser and clean up
    if (browser) {
      await browser.close();
      console.log("🔒 Browser closed");
    }
    
  } catch (error) {
    console.error("❌ DEMO Error:", error.message);
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
  console.error("💥 Unhandled DEMO error:", error.message);
  process.exit(1);
}); 