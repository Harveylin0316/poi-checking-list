# OpenRice 餐厅检查逻辑说明

## 检查项目总览

程序会检查以下6个必需要素：
1. 中文名称
2. 英文名称
3. 门面照片
4. 菜单
5. 餐点照片
6. 相关影片

---

## 详细检查逻辑

### 1. 中文名称检查

**检查方式**: 在主页面查找

**查找位置**:
- `h1[class*="name"]`
- `.restaurant-name`
- `h1`
- `[class*="中文"]`
- `[data-name]`
- `.poi-name`
- `[class*="poi-name"]`

**判断标准**: 
- 文本中包含中文字符（\u4e00-\u9fff）

---

### 2. 英文名称检查

**检查方式**: 在主页面查找

**查找位置**:
- `.pdhs-en-section` ⭐ OpenRice特定的英文名称类
- `[class*="pdhs-en-section"]`
- `[class*="english"]`
- `[class*="en-name"]`
- `[class*="english-name"]`
- `h2`
- `.restaurant-name-en`
- `[class*="name-en"]`

**判断标准**:
- 至少3个英文字符
- 英文字符数 > 中文字符数 × 1.5
- 避免将纯中文名称误判为英文

---

### 3. 门面照片检查

**检查URL**: `餐厅URL/photos/decor`

**检查方式**:
1. 访问 `/photos/decor` 页面
2. 查找照片列表容器中的图片
3. 检查是否有实际照片（排除placeholder、logo、avatar）

**判断标准**:
- 至少1张有效照片（OpenRice的图片URL：`orstatic.com`、`userphoto`、`/photo/`）
- 排除placeholder图片

---

### 4. 菜单检查

**检查URL**: `餐厅URL/menus`

**检查方式**:
1. 访问 `/menus` 页面
2. 先检查是否有"没有菜单"的提示（如"此餐廳暫時沒有菜單"）
3. 查找菜单照片
4. 排除门面照片（doorphoto）

**判断标准**:
- 至少1张有效菜单照片
- 排除门面照片（doorphoto）
- 排除空状态提示

**空状态关键词**:
- "此餐廳暫時沒有菜單"
- "此餐厅暂时没有菜单"
- "暫無菜單"
- "没有菜单"
- "no menu"
- 等

---

### 5. 餐点照片检查

**检查URL**: `餐厅URL/photos/food`

**检查方式**:
1. 访问 `/photos/food` 页面
2. 查找照片列表容器中的图片
3. 检查是否有实际照片

**判断标准**:
- 至少1张有效照片（OpenRice的图片URL）
- 排除placeholder图片

---

### 6. 相关影片检查

**检查URL**: `餐厅URL/photos/videos`

**检查方式**:
1. 访问 `/photos/videos` 页面
2. 检查 `<video>` 标签
3. 检查有效的 `<iframe>`（YouTube、Vimeo、TikTok、Instagram等）
4. 检查视频容器中的视频缩略图

**判断标准**:
- 有 `<video>` 标签，或
- 有有效的视频iframe，或
- 有视频缩略图（`c-vod.orstatic.com` 或明确标记为视频的图片）
- **排除门面照片**（doorphoto）

**视频平台识别**:
- YouTube
- Vimeo
- TikTok
- Instagram
- Youku
- 等

---

## 技术细节

### URL路径规则
- 门面照片: `.../photos/decor`
- 菜单照片: `.../menus`
- 餐点照片: `.../photos/food`
- 相关影片: `.../photos/videos`

### 图片识别规则
- 有效图片URL包含：`orstatic.com`、`userphoto`、`/photo/`
- 排除：`placeholder`、`logo`、`avatar`、`doorphoto`（门面照片）

### 压缩支持
- 支持 gzip 压缩
- 支持 Brotli (br) 压缩（自动回退到gzip）

### 错误处理
- 自动处理超时和网络错误
- 支持Selenium模式（处理JavaScript动态内容）
