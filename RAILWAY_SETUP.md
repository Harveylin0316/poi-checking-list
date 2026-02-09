# 🚂 Railway 重新部署指南

## ⚠️ 重要：需要重新部署

代码已更新，**需要重新部署**才能启用 Selenium 支持。

---

## 📋 重新部署步骤

### 方法1：在 Railway 中重新部署（推荐）

1. **访问 Railway Dashboard**
   - 登录 https://railway.app
   - 进入你的项目

2. **触发重新部署**
   - 点击项目设置（Settings）
   - 找到 "Redeploy" 或 "Deploy" 按钮
   - 点击重新部署

   或者：
   - 在项目页面，点击 "Deployments" 标签
   - 点击最新的部署记录
   - 点击 "Redeploy"

3. **等待部署完成**
   - 通常需要 3-5 分钟
   - 查看部署日志，确认 Chrome 和 ChromeDriver 安装成功

---

### 方法2：推送新代码触发自动部署

如果 Railway 已连接 GitHub，推送代码会自动触发部署：

```bash
git push origin main
```

---

## ✅ 部署后验证

部署完成后，检查：

1. **查看部署日志**
   - 在 Railway 项目页面查看 "Deployments" → "View Logs"
   - 确认看到：
     - `✓ 已啟用Selenium（可處理JavaScript動態內容）`
     - 或 `使用Railway環境的Chrome: /usr/bin/google-chrome`

2. **测试应用**
   - 访问你的 Railway 应用网址
   - 使用"测试单个URL"功能
   - 测试 URL: `https://s.openrice.com/cHRSmW2pOW700`
   - 应该能看到检查结果（不再是 0/6）

---

## 🔍 如果仍然失败

### 检查1：查看 Railway 日志

在 Railway Dashboard → Deployments → View Logs 中查看：
- 是否有 Selenium 初始化成功的消息
- 是否有 Chrome/ChromeDriver 相关的错误

### 检查2：确认 Dockerfile 被使用

在 Railway 项目设置中：
- 确认 "Build Command" 使用 Dockerfile
- 或者确认 railway.json 中 builder 设置为 "DOCKERFILE"

### 检查3：手动设置环境变量

在 Railway → Variables 中添加：
- `CHROMIUM_PATH=/usr/bin/google-chrome`
- `CHROMEDRIVER_PATH=/usr/local/bin/chromedriver`

---

## 💡 预期结果

部署成功后：
- ✅ Selenium 应该能正常初始化
- ✅ 页面内容长度应该 > 5000 字符（不再是 23 字符）
- ✅ 检查结果应该能正常显示（不再是 0/6）

---

## 🆘 如果 Dockerfile 部署失败

如果 Dockerfile 部署有问题，可以尝试使用 Nixpacks：

1. 在 Railway 项目设置中
2. 将 Builder 改为 "NIXPACKS"
3. 添加环境变量：
   - `NIXPACKS_PYTHON_VERSION=3.9`
4. 重新部署

Nixpacks 会自动检测 Python 项目并安装依赖。
