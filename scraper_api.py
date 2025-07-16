from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import asyncio
import pandas as pd
import traceback
from playwright.async_api import async_playwright

app = FastAPI()
data = []

async def extract_current_page_items(page, market_name):
    items = await page.query_selector_all("#companyList-appender-id > li")
    for li in items:
        try:
            name = await li.query_selector("div.company-name > p")
            symbol = await li.query_selector("div.col-box:has(div.col-name:text('Symbol')) > div.col-value")
            isin = await li.query_selector("div.col-box:has(div.col-name:text('ISIN Code')) > div.col-value")
            data.append({
                "Company Name": await name.inner_text(),
                "Symbol": await symbol.inner_text(),
                "ISIN": await isin.inner_text(),
                "Market": market_name
            })
        except Exception as e:
            print(f"⚠️ Skipping row due to error: {e}")
            continue

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/participants-directory/issuer-directory?locale=en")
        await page.wait_for_timeout(5000)

        async def scrape_market(market_name):
            await page.reload()
            await page.wait_for_timeout(3000)
            await page.get_by_text("Advanced Search").click()
            await page.wait_for_timeout(1000)

            selects = await page.query_selector_all("select")
            for sel in selects:
                options = await sel.query_selector_all("option")
                for opt in options:
                    label = (await opt.inner_text()).strip()
                    if market_name.lower() in label.lower():
                        await sel.select_option(label=label)
                        break

            await page.wait_for_timeout(4000)
            await extract_current_page_items(page, market_name)

            seen = set()
            while True:
                links = await page.query_selector_all("a.button-px.px-btn")
                clicked = False
                for link in links:
                    num = await link.get_attribute("data-page")
                    if num and num not in seen:
                        seen.add(num)
                        await link.click()
                        await page.wait_for_timeout(3000)
                        await extract_current_page_items(page, market_name)
                        clicked = True
                        break
                if not clicked:
                    break

        for market in ["Main Market", "Nomu - Parallel Market"]:
            await scrape_market(market)

        await browser.close()

@app.get("/run-scraper")
async def run_scraper():
    try:
        print("🔄 Starting scraper...")
        data.clear()
        await scrape()
        df = pd.DataFrame(data)
        output_path = "saudi_issuer_data.csv"
        df.to_csv(output_path, index=False)
        print("✅ Scrape complete. Returning CSV...")
        return FileResponse(output_path, media_type="text/csv", filename="saudi_issuer_data.csv")
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error during scraping:\n{error_trace}")
        return JSONResponse(status_code=500, content={"error": error_trace})
