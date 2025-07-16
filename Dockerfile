FROM python:3.11-slim

# System dependencies for Playwright browsers
RUN apt-get update && apt-get install -y     wget gnupg curl ca-certificates fonts-liberation libnss3 libxss1 libasound2     libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgtk-3-0 libgbm1 libpango-1.0-0 libxshmfence1     libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxinerama1 libxcursor1 libxi6 libgl1-mesa-glx libglu1-mesa     && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && python -m playwright install chromium

# Copy source code
COPY . .

# Expose port
EXPOSE 10000

# Start server
CMD ["uvicorn", "scraper_api:app", "--host", "0.0.0.0", "--port", "10000"]
