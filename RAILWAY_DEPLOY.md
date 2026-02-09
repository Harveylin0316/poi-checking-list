# 🚂 Railway 部署指南

## 为什么迁移到 Railway？

Streamlit Cloud **无法访问 OpenRice 网站**，因为：
- OpenRice 使用 JavaScript 动态加载内容
- Streamlit Cloud 不支持浏览器（无法使用 Selenium）
- 网络限制导致无法获取完整页面内容

Railway 的优势：
- ✅ 支持 Python 应用
- ✅ 网络访问限制较少
- ✅ 免费额度充足（每月 $5 免费额度）
- ✅ 部署简单，类似 Streamlit Cloud

---

## 📋 部署步骤

### 步骤1：注册 Railway 账号

1. 访问 https://railway.app
2. 点击 "Login" → "Login with GitHub"
3. 授权 Railway 访问你的 GitHub 账号

### 步骤2：创建新项目

1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择你的仓库：`Harveylin0316/poi-checking-list`
4. Railway 会自动检测到 Python 项目

### 步骤3：配置部署

Railway 会自动：
- 检测到 `requirements.txt`
- 安装所有依赖
- 运行应用

**如果自动检测失败**，手动设置：
- **Build Command**: （留空，Railway 会自动处理）
- **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

### 步骤4：获取应用网址

1. 部署完成后，Railway 会提供一个网址
2. 例如：`https://your-app-name.up.railway.app`
3. 点击网址即可访问应用

---

## 🔧 环境变量（可选）

如果需要配置环境变量：
1. 在 Railway 项目页面点击 "Variables"
2. 添加环境变量（如果需要）

**注意**：当前应用不需要环境变量

---

## 💰 费用说明

- **免费额度**：每月 $5（足够日常使用）
- **超出后**：按使用量付费
- **估算**：检查 1000 间餐厅约消耗 $0.10

---

## ✅ 部署后验证

部署完成后，测试：
1. 访问应用网址
2. 上传 Excel 文件
3. 测试单个 URL
4. 确认可以正常检查餐厅

---

## 🆚 与 Streamlit Cloud 对比

| 功能 | Streamlit Cloud | Railway |
|------|----------------|---------|
| 免费额度 | 无限 | $5/月 |
| 网络访问 | ❌ 限制较多 | ✅ 限制较少 |
| 部署难度 | ⭐ 简单 | ⭐⭐ 简单 |
| 支持 Selenium | ❌ | ✅（可配置） |
| 访问 OpenRice | ❌ 失败 | ✅ 应该可以 |

---

## 🆘 遇到问题？

1. **部署失败**：检查 `requirements.txt` 是否正确
2. **应用无法访问**：检查 Start Command 是否正确
3. **网络问题**：Railway 的网络访问通常比 Streamlit Cloud 好

---

## 📞 其他部署选项

如果 Railway 也不可用，可以考虑：

1. **Render**：https://render.com
   - 免费支持 Python
   - 网络访问较好

2. **本地运行**：
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
