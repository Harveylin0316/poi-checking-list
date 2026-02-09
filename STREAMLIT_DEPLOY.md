# 🚀 Streamlit Cloud 部署指南

## 📋 部署前检查清单

✅ 确保以下文件存在：
- `app.py` - Streamlit应用主程序
- `check_restaurants.py` - 核心检查逻辑
- `requirements.txt` - Python依赖包列表
- `.gitignore` - Git忽略文件配置

---

## 🎯 部署步骤（5分钟完成）

### 步骤1：准备GitHub仓库

1. **在GitHub上创建新仓库**
   - 登录 https://github.com
   - 点击右上角 "+" → "New repository"
   - 仓库名称：例如 `openrice-checker` 或 `restaurant-checker`
   - 选择 Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

2. **上传代码到GitHub**

   在终端执行以下命令：

   ```bash
   # 进入项目目录
   cd "/Users/harveylin/Documents/Cursor Project/Checking list of standard poi"
   
   # 初始化Git（如果还没初始化）
   git init
   
   # 添加所有文件
   git add .
   
   # 提交
   git commit -m "Initial commit: OpenRice restaurant checker"
   
   # 连接到GitHub仓库（替换YOUR_USERNAME和YOUR_REPO_NAME）
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   
   # 推送到GitHub
   git branch -M main
   git push -u origin main
   ```

   **注意**：请将 `YOUR_USERNAME` 替换为你的GitHub用户名，`YOUR_REPO_NAME` 替换为你刚创建的仓库名称。

---

### 步骤2：部署到Streamlit Cloud

1. **访问Streamlit Cloud**
   - 打开 https://share.streamlit.io/
   - 点击 "Sign in with GitHub"
   - 授权Streamlit访问你的GitHub账号

2. **部署应用**
   - 点击 "New app"
   - **Repository（仓库）**：选择你刚创建的仓库
   - **Branch（分支）**：选择 `main`
   - **Main file path（主文件路径）**：输入 `app.py`
   - 点击 "Deploy!"

3. **等待部署完成**
   - 通常需要1-3分钟
   - 部署完成后会显示你的应用网址，例如：`https://your-app-name.streamlit.app`

---

## ✅ 部署完成！

现在你可以：
- 分享网址给同事使用
- 每次更新代码后，Streamlit Cloud会自动重新部署
- 在Streamlit Cloud后台查看使用情况

---

## 🔧 常见问题

### Q: 部署失败怎么办？
A: 检查以下几点：
- `requirements.txt` 格式是否正确
- `app.py` 文件路径是否正确
- 所有依赖包是否都在 `requirements.txt` 中

### Q: 如何更新应用？
A: 只需要：
1. 修改代码
2. 提交到GitHub：`git add .` → `git commit -m "更新说明"` → `git push`
3. Streamlit Cloud会自动重新部署（约1-2分钟）

### Q: 应用网址可以自定义吗？
A: 可以！在Streamlit Cloud设置中可以修改应用名称，网址会相应改变。

### Q: 需要付费吗？
A: 完全免费！Streamlit Cloud提供免费套餐，足够日常使用。

---

## 📞 需要帮助？

如果遇到问题，可以：
1. 查看Streamlit Cloud的日志（在应用页面点击"Manage app"）
2. 检查GitHub仓库中的文件是否正确
3. 确认所有依赖都在 `requirements.txt` 中
