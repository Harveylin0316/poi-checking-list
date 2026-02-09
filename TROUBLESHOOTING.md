# 🔧 故障排除指南

## 502 错误

### 问题：应用部署成功但出现 502 错误

**可能原因**：
1. 端口配置错误（Railway 使用 `$PORT` 环境变量）
2. 应用启动失败
3. 启动命令错误

**解决方案**：
- ✅ 已修复：使用 `$PORT` 环境变量
- ✅ 已修复：添加 `--server.headless=true` 参数
- ✅ 已修复：确保使用正确的启动命令

**检查步骤**：
1. 在 Railway Dashboard → Deployments → View Logs
2. 查看应用是否成功启动
3. 确认看到 "You can now view your Streamlit app in your browser"

---

## 页面内容过短（23 字符）

### 问题：所有检查项目都失败，页面内容只有 23 字符

**原因**：
- OpenRice 使用 JavaScript 动态加载内容
- `requests` 库无法执行 JavaScript
- 需要使用 Selenium

**解决方案**：
- ✅ 已配置：Dockerfile 安装 Chrome
- ✅ 已配置：代码启用 Selenium
- ✅ 已配置：Chrome 选项优化

**验证**：
- 查看日志中是否有 "✓ 已啟用Selenium"
- 页面内容长度应该 > 5000 字符

---

## Selenium 初始化失败

### 问题：日志显示 "Selenium初始化失敗"

**可能原因**：
1. Chrome 未正确安装
2. ChromeDriver 路径错误
3. 权限问题

**解决方案**：
1. 检查 Dockerfile 中 Chrome 是否安装成功
2. 确认环境变量 `CHROMIUM_PATH` 和 `CHROMEDRIVER_PATH` 正确
3. 查看详细错误日志

---

## 检查结果全部失败

### 问题：即使使用 Selenium，所有检查项目仍然失败

**可能原因**：
1. 页面加载时间不够
2. 选择器不正确
3. OpenRice 页面结构变化

**解决方案**：
1. 增加等待时间（已设置为 5 秒）
2. 检查日志中的调试信息
3. 使用测试功能测试单个 URL

---

## 常见错误信息

### "無法獲取頁面: 頁面內容過短"
- **原因**：JavaScript 未执行
- **解决**：确保 Selenium 已启用

### "請求超時"
- **原因**：网络问题或 OpenRice 服务器响应慢
- **解决**：增加超时时间或重试

### "連接錯誤"
- **原因**：Railway 无法访问 OpenRice
- **解决**：检查网络配置或使用代理

---

## 调试技巧

1. **查看 Railway 日志**
   - Railway Dashboard → Deployments → View Logs
   - 查找错误信息和调试输出

2. **使用测试功能**
   - 在应用中测试单个 URL
   - 查看返回的 JSON 结果

3. **检查环境变量**
   - Railway → Variables
   - 确认 `PORT`、`CHROMIUM_PATH` 等正确设置

---

## 需要帮助？

如果问题仍然存在，请提供：
1. Railway 部署日志（特别是错误部分）
2. 测试单个 URL 的结果
3. 具体的错误信息
