# Saudi Exchange Issuer Scraper (FastAPI + Playwright)

This project exposes a `/run-scraper` API endpoint that scrapes Saudi Exchange issuer data (Main + Nomu markets) and returns a CSV.

## 🔧 Local Development

```bash
pip install -r requirements.txt
playwright install
uvicorn scraper_api:app --reload
```

Open in browser:
http://localhost:8000/docs

## 🚀 Deploy on Render

1. Push this repo to GitHub
2. Go to https://render.com
3. Click "New Web Service"
4. Select this repo
5. Confirm settings from `render.yaml`
6. Use the public `/run-scraper` endpoint in a Custom GPT or browser

## 🧠 GPT Integration

You can connect the endpoint like:
`GET https://yourapp.onrender.com/run-scraper`
→ will return the CSV file
