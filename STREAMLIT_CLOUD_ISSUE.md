# Streamlit Cloud 網絡限制問題說明

## 🔍 問題診斷

如果所有餐廳檢查結果都是0/6不合格，很可能是 **Streamlit Cloud 無法訪問 OpenRice 網站**。

### 可能的原因：

1. **網絡限制**
   - Streamlit Cloud 可能阻止對某些外部網站的訪問
   - OpenRice 可能阻止來自 Streamlit Cloud 的請求

2. **JavaScript 動態加載**
   - OpenRice 頁面使用 JavaScript 動態加載內容
   - `requests` 庫無法執行 JavaScript，只能獲取初始 HTML
   - 需要 Selenium，但 Streamlit Cloud 不支持瀏覽器

3. **頁面內容過短**
   - 如果獲取到的頁面內容少於 500 字元，說明沒有獲取到完整內容
   - 這會導致所有檢查項目都失敗

---

## ✅ 解決方案

### 方案1：使用其他部署平台（推薦）

**Railway** (推薦)
- 支持 Python 應用
- 網絡限制較少
- 免費額度充足
- 網址：https://railway.app

**Heroku**
- 經典的 Python 部署平台
- 免費層已取消，需要付費

**Render**
- 免費支持 Python 應用
- 網絡訪問較好
- 網址：https://render.com

### 方案2：本地運行（最可靠）

如果只是內部使用，可以在本地運行：

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行應用
streamlit run app.py
```

### 方案3：使用代理（不推薦）

如果必須使用 Streamlit Cloud，可以嘗試：
- 使用代理服務
- 但這會增加複雜性和成本

---

## 🔧 診斷步驟

1. **查看錯誤信息**
   - 檢查完成後，查看"錯誤詳情"
   - 如果顯示"頁面內容過短"或"連接錯誤"，說明是網絡問題

2. **測試單個 URL**
   - 使用側邊欄的"測試單個URL"功能
   - 查看返回的錯誤信息

3. **檢查 Streamlit Cloud 日誌**
   - 點擊應用右下角的"Manage app"
   - 查看"Logs"標籤
   - 尋找網絡錯誤或超時信息

---

## 📊 預期行為

### 正常情況：
- 頁面內容長度：> 5000 字元
- 檢查結果：部分項目通過（如 5/6）
- 錯誤信息：無或很少

### 網絡限制情況：
- 頁面內容長度：< 500 字元
- 檢查結果：0/6（所有項目失敗）
- 錯誤信息："頁面內容過短"或"連接錯誤"

---

## 💡 建議

**最佳方案**：遷移到 Railway 或 Render
- 這些平台對外部網絡訪問的限制較少
- 部署過程類似 Streamlit Cloud
- 免費額度足夠日常使用

**臨時方案**：本地運行
- 最可靠，但需要每台電腦都安裝 Python
- 適合小團隊內部使用
