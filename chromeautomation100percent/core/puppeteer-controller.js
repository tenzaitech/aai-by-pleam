const puppeteer = require('puppeteer');

class PuppeteerController {
    constructor() {
        this.browser = null;
        this.page = null;
        this.isConnected = false;
    }

    async initialize(options = {}) {
        try {
            const defaultOptions = {
                headless: false,
                defaultViewport: { width: 1920, height: 1080 },
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ],
                ...options
            };

            this.browser = await puppeteer.launch(defaultOptions);
            this.page = await this.browser.newPage();
            this.isConnected = true;

            // Set user agent
            await this.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

            console.log('✅ Puppeteer initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ Puppeteer initialization failed:', error);
            return false;
        }
    }

    async navigateTo(url) {
        if (!this.isConnected) {
            throw new Error('Browser not initialized');
        }
        
        try {
            await this.page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
            console.log(`✅ Navigated to: ${url}`);
            return true;
        } catch (error) {
            console.error(`❌ Navigation failed: ${error.message}`);
            return false;
        }
    }

    async clickElement(selector, options = {}) {
        try {
            await this.page.waitForSelector(selector, { timeout: 10000 });
            await this.page.click(selector, options);
            console.log(`✅ Clicked element: ${selector}`);
            return true;
        } catch (error) {
            console.error(`❌ Click failed: ${error.message}`);
            return false;
        }
    }

    async typeText(selector, text) {
        try {
            await this.page.waitForSelector(selector, { timeout: 10000 });
            await this.page.type(selector, text, { delay: 100 });
            console.log(`✅ Typed text in: ${selector}`);
            return true;
        } catch (error) {
            console.error(`❌ Type failed: ${error.message}`);
            return false;
        }
    }

    async takeScreenshot(path) {
        try {
            await this.page.screenshot({ path, fullPage: true });
            console.log(`✅ Screenshot saved: ${path}`);
            return true;
        } catch (error) {
            console.error(`❌ Screenshot failed: ${error.message}`);
            return false;
        }
    }

    async getPageContent() {
        try {
            const content = await this.page.content();
            return content;
        } catch (error) {
            console.error(`❌ Get content failed: ${error.message}`);
            return null;
        }
    }

    async evaluateJavaScript(code) {
        try {
            const result = await this.page.evaluate(code);
            return result;
        } catch (error) {
            console.error(`❌ JavaScript evaluation failed: ${error.message}`);
            return null;
        }
    }

    async waitForElement(selector, timeout = 10000) {
        try {
            await this.page.waitForSelector(selector, { timeout });
            return true;
        } catch (error) {
            console.error(`❌ Wait for element failed: ${error.message}`);
            return false;
        }
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
            this.isConnected = false;
            console.log('✅ Browser closed');
        }
    }
}

module.exports = PuppeteerController; 