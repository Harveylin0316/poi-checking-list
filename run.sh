#!/bin/bash
# Streamlit应用启动脚本

echo "启动OpenRice餐厅检查Web应用..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
