# 部署指南

## 🚀 推荐方案：Streamlit Cloud（最简单）

Streamlit Cloud是Streamlit官方提供的免费托管服务，最适合非技术人员使用。

### 部署步骤：

1. **将代码推送到GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **访问 Streamlit Cloud**
   - 访问 https://streamlit.io/cloud
   - 使用GitHub账号登录

3. **部署应用**
   - 点击 "New app"
   - 选择您的GitHub仓库
   - 设置：
     - **Main file path**: `app.py`
     - **Python version**: 3.9+
   - 点击 "Deploy"

4. **完成！**
   - 几分钟后，应用会自动部署
   - 您会得到一个公开的URL（如：`https://your-app.streamlit.app`）
   - 可以分享给同事使用

### 优点：
- ✅ 完全免费
- ✅ 专为Streamlit优化
- ✅ 自动更新（每次push代码自动重新部署）
- ✅ 无需服务器配置
- ✅ 界面友好

---

## 🌐 方案2：Netlify部署（需要更多配置）

Netlify主要支持静态网站，对于Python应用需要特殊配置。

### 选项A：使用Netlify Functions

1. **创建前端界面**（已创建 `public/index.html`）
2. **创建Netlify Function**（已创建 `netlify_functions/check_restaurant.py`）
3. **配置Netlify**
   - 在Netlify设置中启用Python Functions
   - 设置构建命令和发布目录

### 选项B：使用Docker + Netlify

使用Docker容器运行Streamlit应用。

---

## 📦 方案3：其他部署选项

### Render（推荐）
- 支持Python应用
- 免费套餐可用
- 简单易用
- 访问：https://render.com

### Railway
- 简单易用
- 有免费额度
- 访问：https://railway.app

### Heroku
- 传统选择
- 可能需要付费
- 访问：https://heroku.com

---

## 💡 给同事的使用说明

### 如果使用Streamlit Cloud：

1. **访问应用URL**（您部署后获得的链接）
2. **上传Excel文件**
   - 点击上传区域或拖拽文件
   - 确保Excel包含"餐厅名称"和"URL"列
3. **开始检查**
   - 点击"开始检查"按钮
   - 等待检查完成（可能需要几分钟）
4. **查看结果**
   - 查看检查结果表格
   - 查看不合格餐厅清单
5. **下载报告**
   - 点击"下载Excel报告"按钮
   - 保存报告文件

### Excel文件格式示例：

| 餐厅名称 | URL |
|---------|-----|
| 某某餐厅 | https://tw.openrice.com/zh/taipei/r-xxx |

---

## 🔧 本地测试

在部署前，可以在本地测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行Streamlit应用
streamlit run app.py

# 浏览器会自动打开 http://localhost:8501
```

---

## 📝 注意事项

1. **网络连接**: 确保服务器可以访问OpenRice网站
2. **检查时间**: 每个餐厅约需1-2秒，大量餐厅需要较长时间
3. **文件大小**: Excel文件不应太大（建议少于1000行）
4. **错误处理**: 如果某些餐厅无法访问，会在报告中标记为"错误"
