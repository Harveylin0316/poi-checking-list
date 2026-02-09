#!/bin/bash
# Railway启动脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Starting Streamlit application..."
echo "PORT: $PORT"
echo "Working directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "=========================================="

# 确保输出立即刷新
export PYTHONUNBUFFERED=1

# 检查文件是否存在
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    ls -la
    exit 1
fi

# 检查Python依赖
echo "Checking Python dependencies..."
python3 -c "import streamlit; import pandas; import check_restaurants; print('All imports successful')" || {
    echo "ERROR: Failed to import required modules"
    exit 1
}

echo "Starting Streamlit server..."

# 启动Streamlit
exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
