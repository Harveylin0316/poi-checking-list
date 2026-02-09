# OpenRice 餐厅要素检查程序 - Web版本

## 🚀 快速开始

### 本地运行

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **运行Web应用**
```bash
streamlit run app.py
```

3. **打开浏览器**
访问 `http://localhost:8501`

---

## 📦 部署到Netlify

**注意**: Netlify主要支持静态网站，不支持直接运行Python/Streamlit应用。

### 方案1: 使用Streamlit Cloud（推荐）

Streamlit Cloud是Streamlit官方提供的免费托管服务：

1. 将代码推送到GitHub
2. 访问 https://streamlit.io/cloud
3. 连接GitHub仓库
4. 一键部署

**优点**: 
- 免费
- 专为Streamlit优化
- 自动更新
- 无需配置

### 方案2: 使用Netlify Functions + 前端

如果需要使用Netlify，可以：
1. 创建前端界面（HTML/JavaScript）
2. 使用Netlify Functions作为后端API
3. 在Functions中调用Python检查逻辑

### 方案3: 其他部署选项

- **Render**: 支持Python应用，免费套餐可用
- **Railway**: 简单易用，有免费额度
- **Heroku**: 传统选择（可能需要付费）

---

## 📋 Excel文件格式

您的Excel文件应包含以下列：

| 餐厅名称 | URL |
|---------|-----|
| 某某餐厅 | https://www.openrice.com/zh/taipei/r-xxx |

**支持的列名**:
- 餐厅名称: `餐厅名称`、`餐廳名稱`、`名称`、`名稱`、`name`
- URL: `URL`、`網址`、`网址`、`url`、`链接`、`連結`

---

## 🎯 使用步骤

1. **上传Excel文件** - 点击上传按钮选择文件
2. **预览文件** - 确认文件格式正确
3. **开始检查** - 点击"开始检查"按钮
4. **查看结果** - 等待检查完成，查看结果表格
5. **下载报告** - 点击下载按钮获取Excel报告

---

## ⚙️ 功能说明

### 检查项目
- ✅ 中文名称
- ✅ 英文名称
- ✅ 门面照片 (`/photos/decor`)
- ✅ 菜单 (`/menus`)
- ✅ 餐点照片 (`/photos/food`)
- ✅ 相关影片 (`/photos/videos`)

### 报告内容
生成的Excel报告包含两个工作表：
- **完整报告**: 所有餐厅的检查结果
- **不合格餐厅**: 只包含不合格的餐厅清单

---

## 🔧 技术说明

- **框架**: Streamlit
- **后端**: Python
- **依赖**: 见 `requirements.txt`

---

## 📝 注意事项

1. 检查过程可能需要一些时间（每个餐厅约1-2秒）
2. 确保网络连接稳定
3. 如果某些页面无法访问，会在报告中标记为"错误"
