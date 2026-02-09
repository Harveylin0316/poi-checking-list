# 📤 推送到GitHub的几种方法

代码已经准备好并提交到本地Git仓库了！现在需要推送到GitHub。

## ✅ 已完成
- ✅ Git仓库已初始化
- ✅ 所有文件已添加
- ✅ 代码已提交
- ✅ 远程仓库已连接

## 🔐 需要认证才能推送

推送代码到GitHub需要身份验证。以下是几种方法：

---

## 方法1：使用GitHub Personal Access Token（推荐）

### 步骤1：创建Token
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 给token起个名字，例如：`poi-checking-list`
4. 选择过期时间（建议选择 "No expiration" 或 "90 days"）
5. 勾选权限：至少需要 `repo` 权限
6. 点击 "Generate token"
7. **重要**：复制生成的token（只显示一次！）

### 步骤2：推送代码
在终端执行：

```bash
cd "/Users/harveylin/Documents/Cursor Project/Checking list of standard poi"
git push -u origin main
```

当提示输入用户名时：
- Username: `Harveylin0316`
- Password: **粘贴刚才复制的token**（不是GitHub密码！）

---

## 方法2：使用GitHub CLI（最简单）

### 步骤1：安装GitHub CLI
```bash
brew install gh
```

### 步骤2：登录
```bash
gh auth login
```
按照提示选择：
- GitHub.com
- HTTPS
- 登录方式（浏览器或token）

### 步骤3：推送
```bash
cd "/Users/harveylin/Documents/Cursor Project/Checking list of standard poi"
git push -u origin main
```

---

## 方法3：使用SSH密钥（适合长期使用）

### 步骤1：检查是否已有SSH密钥
```bash
ls -al ~/.ssh
```

### 步骤2：如果没有，生成SSH密钥
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
（按Enter使用默认设置）

### 步骤3：添加SSH密钥到GitHub
```bash
cat ~/.ssh/id_ed25519.pub
```
复制输出的内容，然后：
1. 访问 https://github.com/settings/keys
2. 点击 "New SSH key"
3. 粘贴密钥内容
4. 点击 "Add SSH key"

### 步骤4：修改远程仓库URL为SSH
```bash
cd "/Users/harveylin/Documents/Cursor Project/Checking list of standard poi"
git remote set-url origin git@github.com:Harveylin0316/poi-checking-list.git
git push -u origin main
```

---

## 🎯 推荐流程

**最快的方法**：使用方法1（Personal Access Token）
1. 创建token（2分钟）
2. 执行推送命令
3. 输入用户名和token
4. 完成！

---

## ✅ 推送成功后

推送成功后，你可以：
1. 访问 https://github.com/Harveylin0316/poi-checking-list 查看代码
2. 然后按照 `STREAMLIT_DEPLOY.md` 的步骤部署到Streamlit Cloud

---

## 🆘 如果遇到问题

**问题：`fatal: could not read Username`**
- 解决方法：使用方法1或方法2进行认证

**问题：`Permission denied`**
- 解决方法：检查token权限是否包含 `repo`

**问题：`remote: Invalid username or password`**
- 解决方法：确保使用token而不是密码（方法1）
