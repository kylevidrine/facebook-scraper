FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libatspi2.0-0 \
    libxrandr2 \
    libasound2 \
    libxdamage1 \
    libxss1 \
    libgconf-2-4 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium --with-deps

# Copy application files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TESSERACT_CMD=/usr/bin/tesseract

# Run as non-root user
RUN useradd -m scraper && chown -R scraper:scraper /app
USER scraper

CMD ["python", "scraper.py"]