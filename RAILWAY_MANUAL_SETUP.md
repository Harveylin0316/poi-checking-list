# 🚂 Railway 手动配置指南（502错误修复）

## ⚠️ 重要：Railway可能没有读取railway.json

如果应用仍然502错误，需要在Railway Dashboard中**手动设置启动命令**。

---

## 📋 手动设置步骤

### 步骤1：进入Railway项目设置

1. 登录 https://railway.app
2. 进入你的项目
3. 点击 **"Settings"** 标签

### 步骤2：设置启动命令

1. 找到 **"Deploy"** 部分
2. 找到 **"Custom Start Command"** 或 **"Start Command"**
3. **删除**现有的命令（如果有）
4. **输入以下命令**：
   ```
   ./start.sh
   ```
   或者：
   ```
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
   ```

5. 点击 **"Save"** 或 **"Deploy"**

### 步骤3：重新部署

1. 在项目页面点击 **"Redeploy"**
2. 或等待自动重新部署
3. 查看部署日志确认应用启动成功

---

## 🔍 检查部署日志

部署完成后，查看日志应该看到：

```
Starting Streamlit application...
PORT: 8080
（或其他端口号）

You can now view your Streamlit app in your browser.

Local URL: http://0.0.0.0:8080
Network URL: http://172.x.x.x:8080
```

如果看到这些信息，说明应用已成功启动。

---

## 🆘 如果仍然502

### 检查1：查看完整日志

在 Railway Dashboard → Deployments → View Logs：
- 查看是否有Python错误
- 查看是否有导入错误
- 查看是否有端口错误

### 检查2：确认启动脚本权限

如果使用 `./start.sh`，确保脚本有执行权限：
- Dockerfile中已设置 `RUN chmod +x start.sh`
- 如果仍然失败，尝试使用完整命令而不是脚本

### 检查3：尝试简化启动命令

如果复杂命令失败，尝试最简单的：
```
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## 💡 替代方案：使用Nixpacks

如果Dockerfile有问题，可以尝试使用Nixpacks：

1. Railway Dashboard → Settings
2. 将 Builder 改为 **"NIXPACKS"**
3. 设置 Start Command：
   ```
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
   ```
4. 重新部署

Nixpacks会自动检测Python项目并安装依赖。

---

## 📞 需要帮助？

如果问题仍然存在，请提供：
1. Railway部署日志的最后100行
2. Settings中的Start Command设置
3. 是否有任何Python错误信息
