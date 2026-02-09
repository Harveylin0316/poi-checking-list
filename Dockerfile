# 使用Python官方镜像
FROM python:3.9-slim

# 安裝系統依賴（包括Chrome和ChromeDriver）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 安裝Google Chrome（使用新方法，不依賴apt-key）
RUN wget -q -O /tmp/google-chrome-stable.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome-stable.deb \
    && rm /tmp/google-chrome-stable.deb \
    && rm -rf /var/lib/apt/lists/*

# 安裝ChromeDriver（使用webdriver-manager自動管理，更簡單可靠）
# ChromeDriver會在運行時自動下載匹配的版本

# 設置工作目錄
WORKDIR /app

# 複製requirements文件
COPY requirements.txt .

# 安裝Python依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用文件
COPY . .

# 設置啟動腳本權限
RUN chmod +x start.sh

# 設置環境變量
ENV CHROMIUM_PATH=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV PYTHONUNBUFFERED=1

# 暴露端口（Railway會自動設置PORT環境變量）
EXPOSE 8080

# 啟動Streamlit應用
# Railway的startCommand會覆蓋這個CMD，但如果沒有設置則使用這個
CMD ["./start.sh"]
