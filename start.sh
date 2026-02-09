#!/bin/bash
# Railway启动脚本

echo "Starting Streamlit application..."
echo "PORT: $PORT"

# 确保输出立即刷新
export PYTHONUNBUFFERED=1

# 启动Streamlit
exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
