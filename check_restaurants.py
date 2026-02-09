import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import json
from datetime import datetime

# 尝试导入brotli（可选，用于解压Brotli压缩的响应）
try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

# 尝试导入Selenium（可选）
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("警告: Selenium未安装，将使用requests（可能无法处理JavaScript动态内容）")

class OpenRiceChecker:
    def __init__(self, excel_file, use_selenium=True):
        """
        初始化检查器
        :param excel_file: Excel文件路径，应包含餐厅名称和URL列
        :param use_selenium: 是否使用Selenium（推荐True，可处理JavaScript动态内容）
        """
        self.excel_file = excel_file
        self.results = []
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        
        if self.use_selenium:
            # 设置Chrome选项
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✓ 已启用Selenium（可处理JavaScript动态内容）")
            except Exception as e:
                print(f"警告: Selenium初始化失败: {e}，将使用requests")
                self.use_selenium = False
                self.driver = None
        else:
            self.driver = None
        
        if not self.use_selenium:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8'
            })
    
    def __del__(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def load_restaurants(self):
        """从Excel加载餐厅数据"""
        try:
            df = pd.read_excel(self.excel_file)
            # 检查必要的列是否存在
            if 'URL' not in df.columns:
                # 尝试其他可能的列名
                possible_url_cols = ['網址', '网址', 'url', '链接', '連結']
                url_col = None
                for col in possible_url_cols:
                    if col in df.columns:
                        url_col = col
                        break
                if url_col:
                    df['URL'] = df[url_col]
                else:
                    raise ValueError("Excel文件必须包含'URL'列（或'網址'、'网址'等）")
            
            if '餐厅名称' not in df.columns:
                # 尝试其他可能的列名
                possible_name_cols = ['餐廳名稱', '餐厅名称', '名稱', '名称', 'name', 'Name']
                name_col = None
                for col in possible_name_cols:
                    if col in df.columns:
                        name_col = col
                        break
                if name_col:
                    df['餐厅名称'] = df[name_col]
                else:
                    raise ValueError("Excel文件必须包含'餐厅名称'列（或'餐廳名稱'、'名称'等）")
            
            return df
        except Exception as e:
            print(f"读取Excel文件错误: {e}")
            return None
    
    def check_chinese_name(self, soup):
        """检查中文餐厅名称"""
        # OpenRice通常使用特定的class或id来显示中文名称
        selectors = [
            'h1[class*="name"]',
            '.restaurant-name',
            'h1',
            '[class*="中文"]',
            '[data-name]',
            '.poi-name',
            '[class*="poi-name"]'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # 检查是否包含中文字符
                if text and any('\u4e00' <= char <= '\u9fff' for char in text):
                    return True, text
        return False, None
    
    def check_english_name(self, soup):
        """检查英文餐厅名称"""
        # 查找英文名称，通常在中文名称附近或特定位置
        selectors = [
            '.pdhs-en-section',  # OpenRice特定的英文名称类
            '[class*="pdhs-en-section"]',
            '[class*="english"]',
            '[class*="en-name"]',
            '[class*="english-name"]',
            'h2',
            '.restaurant-name-en',
            '[class*="name-en"]'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text:
                    # 检查是否主要是英文字符（至少50%是英文字母）
                    english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
                    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
                    total_chars = len([c for c in text if c.isalnum()])
                    
                    # 必须主要是英文（英文字符数 > 中文字符数，且至少3个英文字符）
                    if total_chars > 0 and english_chars >= 3 and english_chars > chinese_chars:
                        return True, text
        
        # 检查h1标签中是否同时包含中英文
        h1 = soup.select_one('h1')
        if h1:
            text = h1.get_text(strip=True)
            if text:
                # 检查英文和中文的比例
                english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
                chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
                
                # 如果英文字符数明显多于中文字符数，且至少3个英文字符
                if english_chars >= 3 and english_chars > chinese_chars * 1.5:
                    # 提取英文部分
                    words = text.split()
                    english_words = [w for w in words if w.isalpha() and len(w) >= 2]
                    if english_words:
                        return True, ' '.join(english_words)
        
        return False, None
    
    def check_category_page(self, base_url, category_path):
        """检查特定分类页面是否有实际照片或影片
        category_path: 'decor', 'menu', 'food', 'videos'
        """
        try:
            # 构建分类页面URL
            if '/photos' in base_url:
                # 如果已经是photos页面，替换路径
                category_url = base_url.rsplit('/photos', 1)[0] + '/photos/' + category_path
            else:
                category_url = base_url.rstrip('/') + '/photos/' + category_path
            
            soup = self.get_page_soup(category_url)
            
            # 对于videos分类，检查是否有实际的视频
            if category_path == 'videos':
                # 检查video标签
                videos = soup.find_all('video')
                if len(videos) > 0:
                    return True
                
                # 检查iframe是否有有效的视频源
                iframes = soup.find_all('iframe')
                for iframe in iframes:
                    src = iframe.get('src', '')
                    if src and any(platform in src.lower() for platform in ['youtube', 'vimeo', 'video', 'youku', 'tiktok', 'instagram']):
                        return True
                
                # 检查视频容器中是否有视频缩略图
                video_containers = soup.select('[class*="video"], [class*="reel"], [class*="media"]')
                video_thumbnail_count = 0
                for container in video_containers:
                    imgs = container.find_all('img')
                    for img in imgs:
                        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                        if src:
                            # 排除placeholder、logo、avatar和门面照片
                            if ('placeholder' not in src.lower() and 
                                'logo' not in src.lower() and
                                'avatar' not in src.lower() and
                                'doorphoto' not in src.lower() and  # 排除门面照片
                                ('http' in src or src.startswith('//'))):
                                # 检查是否是OpenRice的视频相关图片（视频CDN）
                                if ('c-vod.orstatic.com' in src or  # 视频CDN
                                    ('orstatic.com' in src and '/video/' in src.lower()) or
                                    ('orstatic.com' in src and 'reel' in src.lower())):
                                    # 进一步检查alt属性，排除门面照片
                                    alt = img.get('alt', '').lower()
                                    if 'door' not in alt and '門面' not in alt and '门面' not in alt:
                                        video_thumbnail_count += 1
                
                # 如果有视频缩略图，认为有视频
                if video_thumbnail_count > 0:
                    return True
                
                # 如果没有video、有效的iframe或视频缩略图，返回False
                return False
            
            # 对于照片分类（decor, menu, food），检查是否有实际照片
            # 检查是否有实际的照片（不是placeholder）
            photo_list_selectors = [
                '[class*="media-list"]',
                '[class*="photo-list"]',
                '[class*="image-list"]',
                '[class*="gallery"]',
                '[class*="photo-grid"]'
            ]
            
            photo_count = 0
            
            # 方法1: 检查照片列表容器中的图片
            for selector in photo_list_selectors:
                containers = soup.select(selector)
                for container in containers:
                    imgs = container.find_all('img')
                    for img in imgs:
                        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                        if src:
                            # 排除placeholder图片
                            if ('placeholder' not in src.lower() and 
                                'logo' not in src.lower() and
                                'avatar' not in src.lower() and
                                ('http' in src or src.startswith('//'))):
                                # 检查是否是OpenRice的图片URL
                                if ('orstatic.com' in src or 
                                    '/photo/' in src or
                                    'userphoto' in src):
                                    photo_count += 1
            
            # 方法2: 如果照片列表容器中没有找到，检查所有图片
            if photo_count == 0:
                all_imgs = soup.find_all('img')
                for img in all_imgs:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                    if src:
                        # 排除placeholder和logo等非照片图片
                        if ('placeholder' not in src.lower() and 
                            'logo' not in src.lower() and
                            'avatar' not in src.lower() and
                            ('http' in src or src.startswith('//'))):
                            # 检查是否是用户上传的照片
                            if ('userphoto' in src or 
                                '/photo/' in src or
                                'orstatic.com/userphoto' in src):
                                photo_count += 1
            
            # 至少需要1张实际照片才算有照片
            return photo_count > 0
            
        except Exception as e:
            print(f"  检查分类页面 '/photos/{category_path}' 时出错: {e}")
            return False
    
    def check_facade_photo(self, soup, base_url=None):
        """检查门面照片（通过检查 /photos/decor 页面）"""
        if base_url:
            # 检查 /photos/decor 页面是否有照片
            return self.check_category_page(base_url, 'decor')
        
        # 备用方法：在主页面查找
        img_selectors = [
            'img[class*="facade"]',
            'img[class*="exterior"]',
            'img[alt*="門面"]',
            'img[alt*="外观"]',
            'img[alt*="外觀"]',
            'img[alt*="環境"]',
            '.restaurant-photo img',
            '.main-photo img',
            '[class*="main-photo"] img',
            '[class*="cover-photo"] img'
        ]
        
        for selector in img_selectors:
            img = soup.select_one(selector)
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and 'http' in src:
                    return True
        
        return False
    
    def check_menu(self, soup, base_url=None):
        """检查菜单照片（通过检查 /menus 页面）"""
        if base_url:
            try:
                # 构建菜单页面URL
                if '/photos' in base_url:
                    # 如果已经是photos页面，替换路径
                    menu_url = base_url.rsplit('/photos', 1)[0] + '/menus'
                else:
                    menu_url = base_url.rstrip('/') + '/menus'
                
                menu_soup = self.get_page_soup(menu_url)
                
                # 先检查是否有"没有菜单"的提示
                menu_text = menu_soup.get_text()
                empty_keywords = [
                    '此餐廳暫時沒有菜單',
                    '此餐厅暂时没有菜单',
                    '暫無菜單',
                    '暂无菜单',
                    '沒有菜單',
                    '没有菜单',
                    '尚無菜單',
                    '尚无菜单',
                    'no menu',
                    '暫時沒有',
                    '暂时没有'
                ]
                for keyword in empty_keywords:
                    if keyword in menu_text:
                        return False  # 明确提示没有菜单
                
                # 检查是否有空状态的class或id
                empty_selectors = [
                    '[class*="empty"]',
                    '[class*="no-menu"]',
                    '[class*="no_menu"]',
                    '[id*="empty"]',
                    '[id*="no-menu"]'
                ]
                for selector in empty_selectors:
                    empty_elements = menu_soup.select(selector)
                    if empty_elements:
                        # 检查这些元素中是否包含"没有菜单"的文本
                        for elem in empty_elements:
                            elem_text = elem.get_text()
                            if any(keyword in elem_text for keyword in empty_keywords):
                                return False
                
                # 检查是否有实际的照片（不是placeholder）
                photo_list_selectors = [
                    '[class*="media-list"]',
                    '[class*="photo-list"]',
                    '[class*="image-list"]',
                    '[class*="gallery"]',
                    '[class*="photo-grid"]'
                ]
                
                photo_count = 0
                
                # 方法1: 检查照片列表容器中的图片
                for selector in photo_list_selectors:
                    containers = menu_soup.select(selector)
                    for container in containers:
                        imgs = container.find_all('img')
                        for img in imgs:
                            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                            if src:
                                # 排除placeholder图片
                                if ('placeholder' not in src.lower() and 
                                    'logo' not in src.lower() and
                                    'avatar' not in src.lower() and
                                    ('http' in src or src.startswith('//'))):
                                    # 检查是否是OpenRice的图片URL，排除门面照片
                                    if ('orstatic.com' in src or 
                                        '/photo/' in src or
                                        'userphoto' in src):
                                        # 排除门面照片（doorphoto）
                                        if 'doorphoto' not in src.lower():
                                            alt = img.get('alt', '').lower()
                                            if 'door' not in alt and '門面' not in alt and '门面' not in alt:
                                                photo_count += 1
                
                # 方法2: 如果照片列表容器中没有找到，检查所有图片
                if photo_count == 0:
                    all_imgs = menu_soup.find_all('img')
                    for img in all_imgs:
                        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                        if src:
                            # 排除placeholder和logo等非照片图片
                            if ('placeholder' not in src.lower() and 
                                'logo' not in src.lower() and
                                'avatar' not in src.lower() and
                                ('http' in src or src.startswith('//'))):
                                # 检查是否是用户上传的照片，排除门面照片
                                if ('userphoto' in src or 
                                    '/photo/' in src or
                                    'orstatic.com/userphoto' in src):
                                    # 排除门面照片（doorphoto）
                                    if 'doorphoto' not in src.lower():
                                        alt = img.get('alt', '').lower()
                                        if 'door' not in alt and '門面' not in alt and '门面' not in alt:
                                            photo_count += 1
                
                # 至少需要1张实际照片才算有照片
                return photo_count > 0
                
            except Exception as e:
                print(f"  检查菜单页面 '/menus' 时出错: {e}")
                return False
        
        # 备用方法：在主页面查找（仅作为最后手段）
        menu_keywords = ['menu', '菜單', '菜单', '餐牌', '菜譜', '菜谱']
        menu_selectors = [
            '[class*="menu"]',
            '[id*="menu"]',
            'a[href*="menu"]',
            '[class*="菜單"]',
            '[class*="菜谱"]'
        ]
        
        for selector in menu_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True).lower()
                if any(keyword in text for keyword in menu_keywords):
                    # 注意：主页面找到菜单关键词不能保证有菜单照片，返回False
                    return False
        
        return False
    
    def check_food_photos(self, soup, base_url=None):
        """检查餐点照片（通过检查 /photos/food 页面）"""
        if base_url:
            # 检查 /photos/food 页面是否有照片
            return self.check_category_page(base_url, 'food')
        
        # 备用方法：在主页面查找
        food_keywords = ['food', 'dish', '餐點', '餐点', '美食', '菜式', '菜品', '料理', '食物']
        imgs = soup.find_all('img')
        
        food_photo_count = 0
        for img in imgs:
            src = img.get('src', '') or img.get('data-src', '') or img.get('data-lazy-src', '')
            alt = img.get('alt', '').lower()
            class_name = ' '.join(img.get('class', [])).lower()
            
            if src and 'http' in src:
                if (any(keyword in alt for keyword in food_keywords) or 
                   any(keyword in class_name for keyword in food_keywords)):
                    food_photo_count += 1
        
        # 如果有多个餐点照片，认为有餐点照片
        return food_photo_count >= 2
    
    def check_videos(self, soup, base_url=None):
        """检查相关影片（通过检查 /photos/videos 页面）"""
        if base_url:
            # 检查 /photos/videos 页面是否有实际视频
            return self.check_category_page(base_url, 'videos')
        
        # 备用方法：在主页面查找
        # 查找视频元素
        video_selectors = [
            'video',
            'iframe[src*="youtube"]',
            'iframe[src*="vimeo"]',
            'iframe[src*="video"]',
            '[class*="video"]',
            '[id*="video"]',
            '[class*="youtube"]'
        ]
        
        for selector in video_selectors:
            elements = soup.select(selector)
            if elements:
                return True
        
        # 检查是否有视频相关的链接
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            if any(platform in href for platform in ['youtube', 'vimeo', 'video', 'youku']):
                return True
        
        # 检查是否有视频相关的文字
        video_keywords = ['影片', '视频', 'video', 'youtube']
        all_text = soup.get_text().lower()
        if any(keyword in all_text for keyword in video_keywords):
            # 进一步检查是否有实际的视频元素
            if soup.find('video') or soup.find('iframe'):
                return True
        
        return False
    
    def get_page_soup(self, url):
        """获取页面的BeautifulSoup对象"""
        if self.use_selenium and self.driver:
            try:
                self.driver.get(url)
                # 等待页面加载
                time.sleep(3)  # 等待JavaScript执行
                # 尝试等待特定元素加载
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except:
                    pass
                html = self.driver.page_source
                return BeautifulSoup(html, 'html.parser')
            except Exception as e:
                print(f"  Selenium获取页面失败: {e}，尝试使用requests")
                # 如果Selenium失败，回退到requests
                pass
        
        # 使用requests作为备选
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # 检查Content-Encoding，如果是br (Brotli)，尝试解压
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            if content_encoding == 'br':
                # 尝试使用brotli解压
                if BROTLI_AVAILABLE:
                    try:
                        content = brotli.decompress(response.content)
                        return BeautifulSoup(content.decode('utf-8', errors='ignore'), 'html.parser')
                    except Exception as e:
                        # 如果解压失败，重新请求不使用br压缩
                        pass
                
                # 如果没有brotli库或解压失败，重新请求不使用br压缩
                headers = self.session.headers.copy()
                headers['Accept-Encoding'] = 'gzip, deflate'
                no_br_response = requests.get(url, headers=headers, timeout=15)
                no_br_response.raise_for_status()
                return BeautifulSoup(no_br_response.content, 'html.parser')
            
            # 正常情况（gzip或其他）
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            raise Exception(f"无法获取页面: {e}")
    
    def check_restaurant(self, url, restaurant_name):
        """检查单个餐厅的所有要素"""
        print(f"正在检查: {restaurant_name} - {url}")
        
        try:
            soup = self.get_page_soup(url)
            
            checks = {
                '中文名称': self.check_chinese_name(soup),
                '英文名称': self.check_english_name(soup),
                '门面照片': self.check_facade_photo(soup, base_url=url),
                '菜单': self.check_menu(soup, base_url=url),
                '餐点照片': self.check_food_photos(soup, base_url=url),
                '相关影片': self.check_videos(soup, base_url=url)
            }
            
            # 统计通过和失败的检查项
            def is_passed(check_result):
                """判断检查结果是否通过"""
                if isinstance(check_result, tuple):
                    return check_result[0]  # 元组的第一个元素表示是否通过
                else:
                    return bool(check_result)  # 布尔值直接判断
            
            passed = sum(1 for result in checks.values() if is_passed(result))
            total = len(checks)
            
            result = {
                '餐厅名称': restaurant_name,
                'URL': url,
                '检查时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '通过率': f"{passed}/{total}",
                '状态': '合格' if passed == total else '不合格',
                **{key: ('✓' if is_passed(val) else '✗') 
                    for key, val in checks.items()}
            }
            
            return result
            
        except requests.exceptions.Timeout:
            print(f"请求超时: {restaurant_name}")
            return {
                '餐厅名称': restaurant_name,
                'URL': url,
                '检查时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '状态': '错误',
                '错误信息': '请求超时'
            }
        except requests.exceptions.RequestException as e:
            print(f"请求错误 {restaurant_name}: {e}")
            return {
                '餐厅名称': restaurant_name,
                'URL': url,
                '检查时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '状态': '错误',
                '错误信息': f'请求错误: {str(e)}'
            }
        except Exception as e:
            print(f"检查 {restaurant_name} 时出错: {e}")
            return {
                '餐厅名称': restaurant_name,
                'URL': url,
                '检查时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '状态': '错误',
                '错误信息': str(e)
            }
    
    def run_check(self, delay=1):
        """运行所有检查"""
        df = self.load_restaurants()
        if df is None:
            return
        
        print(f"开始检查 {len(df)} 间餐厅...")
        print("-" * 60)
        
        for idx, row in df.iterrows():
            restaurant_name = row['餐厅名称']
            url = row['URL']
            
            # 确保URL是完整的
            if not url.startswith('http'):
                url = 'https://' + url
            
            result = self.check_restaurant(url, restaurant_name)
            self.results.append(result)
            
            # 延迟以避免请求过快
            time.sleep(delay)
            
            status_icon = '✓' if result.get('状态') == '合格' else '✗'
            print(f"{status_icon} {restaurant_name} - {result.get('状态', '未知')}")
        
        print("-" * 60)
        print("\n检查完成！")
    
    def generate_report(self, output_file='restaurant_check_report.xlsx'):
        """生成检查报告"""
        if not self.results:
            print("没有检查结果可生成报告")
            return
        
        df_results = pd.DataFrame(self.results)
        
        # 分离合格和不合格的餐厅
        failed_restaurants = df_results[df_results['状态'] != '合格']
        
        # 保存完整报告
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_results.to_excel(writer, sheet_name='完整报告', index=False)
            if len(failed_restaurants) > 0:
                failed_restaurants.to_excel(writer, sheet_name='不合格餐厅', index=False)
        
        print(f"\n报告已生成: {output_file}")
        print(f"总餐厅数: {len(df_results)}")
        print(f"合格餐厅: {len(df_results[df_results['状态'] == '合格'])}")
        print(f"不合格餐厅: {len(failed_restaurants)}")
        
        # 打印不合格餐厅清单
        if len(failed_restaurants) > 0:
            print("\n不合格餐厅清单:")
            print("=" * 60)
            for idx, row in failed_restaurants.iterrows():
                print(f"\n{idx + 1}. {row['餐厅名称']}")
                print(f"   URL: {row['URL']}")
                print(f"   状态: {row['状态']}")
                if '通过率' in row:
                    print(f"   通过率: {row['通过率']}")
                if '错误信息' in row and pd.notna(row['错误信息']):
                    print(f"   错误: {row['错误信息']}")
            print("=" * 60)


def main():
    # 使用示例
    excel_file = 'restaurants.xlsx'  # 请替换为您的Excel文件路径
    use_selenium = True  # 设置为True使用Selenium（需要Chrome浏览器），False使用requests
    
    print("=" * 60)
    print("OpenRice 餐厅要素检查程序")
    print("=" * 60)
    
    checker = OpenRiceChecker(excel_file, use_selenium=use_selenium)
    checker.run_check(delay=2 if use_selenium else 1)  # Selenium模式需要更长的延迟
    checker.generate_report('restaurant_check_report.xlsx')
    
    # 清理资源
    if checker.driver:
        checker.driver.quit()


if __name__ == '__main__':
    main()
