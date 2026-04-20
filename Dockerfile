FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

ARG ENV=test
ARG PROJECT=workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl gnupg unzip default-jre \
    fonts-liberation libnss3 libnspr4 libx11-6 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
    libxi6 libxss1 libxshmfence1 libgbm1 libgtk-3-0 \
    libatk1.0-0 libatk-bridge2.0-0 libdrm2 xdg-utils \
    && wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y /tmp/google-chrome.deb \
    && rm -rf /tmp/google-chrome.deb /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py", "-env", "${ENV}", "-driver_type", "chrome-headless", "-report", "yes", "-open", "no", "-project", "${PROJECT}"]