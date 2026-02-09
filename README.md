# OpenRice 餐厅要素检查程序

## 功能
检查OpenRice网站上餐厅页面是否包含以下必需元素：
- ✅ 餐厅名称（中文与英文）
- ✅ 门面照片
- ✅ 菜单
- ✅ 餐点照片
- ✅ 相关影片

## 工作原理

程序会**访问每个餐厅的URL**，然后解析HTML页面来查找各项元素：

1. **访问主页面**: 检查餐厅名称（中文和英文）
2. **访问照片页面**: 自动访问 `/photos` 页面检查照片相关要素
3. **检查分类**: 在照片页面中查找以下分类标签：
   - **门面照片**: 检查是否有"環境"分类
   - **菜单**: 检查是否有"菜單"分类
   - **餐点照片**: 检查是否有"食物"分类
   - **相关影片**: 检查是否有"影片"分类
4. **解析HTML**: 使用 `BeautifulSoup` 解析页面HTML内容（支持Selenium处理JavaScript动态内容）
5. **生成报告**: 将检查结果整理成Excel报告

### 检查逻辑说明

- **主页面检查**: 餐厅名称（中文与英文）
- **照片页面检查**: 通过访问 `餐厅URL/photos` 页面，检查是否存在相应的分类标签
  - **门面照片**: 检查"環境"分类下是否有实际照片（排除placeholder）
  - **菜单**: 
    1. 先检查照片页面的"菜單"分类是否有照片
    2. 如果没有，访问菜单页面（`/menu/餐厅ID/takeaway`）检查是否有菜单照片
    3. 至少需要1张实际菜单照片才算通过
  - **餐点照片**: 检查"食物"分类下是否有实际照片（排除placeholder）
  - **相关影片**: 检查"影片"分类下是否有实际照片（排除placeholder）
  
**重要**: 所有照片检查都会排除placeholder、logo、avatar等非实际照片，只计算用户上传的真实照片。

## 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: 
- **Selenium模式（推荐）**: 可处理JavaScript动态加载的内容，但需要安装Chrome浏览器
  - macOS: 从App Store或Google官网安装Chrome
  - Windows: 从Google官网下载安装Chrome
  - Selenium会自动下载ChromeDriver，首次运行可能需要一些时间
  
- **Requests模式**: 如果不想安装Chrome，可以在代码中设置 `use_selenium=False`
  - 注意：可能无法检测到JavaScript动态加载的内容

**测试结果说明**:
根据测试，OpenRice网站使用JavaScript动态加载内容，建议使用Selenium模式以获得更准确的检查结果。

## Excel文件格式

您的Excel文件应包含以下列（支持多种列名）：
- `餐厅名称` 或 `餐廳名稱` 或 `名称` 或 `名稱` 或 `name`
- `URL` 或 `網址` 或 `网址` 或 `url` 或 `链接` 或 `連結`

示例：
| 餐厅名称 | URL |
|---------|-----|
| 某某餐厅 | https://www.openrice.com/zh/hongkong/r-xxx |

## 使用方法

### 方式1：Web应用（推荐，最简单）

1. **访问Web应用**
   - 部署到Streamlit Cloud后，访问应用网址
   - 或本地运行：`streamlit run app.py`

2. **使用步骤**
   - 上传Excel文件
   - 点击"开始检查"
   - 等待检查完成
   - 下载报告

### 方式2：命令行（本地使用）

1. 将您的Excel文件放在项目目录中，命名为 `restaurants.xlsx`（或修改代码中的文件名）

2. 运行程序：
```bash
python check_restaurants.py
```

3. 程序会：
   - 读取Excel文件
   - 逐个访问每个餐厅页面
   - 检查所有必需元素
   - 生成报告文件 `restaurant_check_report.xlsx`

## 报告说明

生成的Excel报告包含两个工作表：
- **完整报告**: 所有餐厅的检查结果
- **不合格餐厅**: 只包含不合格的餐厅清单

每行包含：
- 餐厅名称
- URL
- 检查时间
- 通过率（如：6/7）
- 状态（合格/不合格）
- 各项检查结果（✓ 或 ✗）

## 部署到Streamlit Cloud

详细部署步骤请参考：[STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)

快速步骤：
1. 将代码推送到GitHub
2. 访问 https://share.streamlit.io/
3. 连接GitHub仓库
4. 一键部署

## 注意事项

1. 程序会在每次请求之间延迟1秒，避免请求过快
2. 如果OpenRice网站结构发生变化，可能需要调整选择器
3. 某些动态加载的内容可能需要使用Selenium而不是BeautifulSoup
4. 确保网络连接稳定，程序会自动处理超时和错误
5. Web应用版本默认不使用Selenium（Streamlit Cloud环境限制），如需Selenium功能请在本地运行
