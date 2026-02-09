# 使用Python官方镜像
FROM python:3.9-slim

# 安裝系統依賴（包括Chrome和ChromeDriver）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
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

# 設置環境變量
ENV CHROMIUM_PATH=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# 暴露端口
EXPOSE 8501

# 啟動Streamlit應用
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
