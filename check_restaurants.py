import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import json
from datetime import datetime

# 嘗試匯入brotli（可選，用於解壓Brotli壓縮的回應）
try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

# 嘗試匯入Selenium（可選）
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
    print("警告: Selenium未安裝，將使用requests（可能無法處理JavaScript動態內容）")

class OpenRiceChecker:
    def __init__(self, excel_file, use_selenium=True):
        """
        初始化檢查器
        :param excel_file: Excel檔案路徑，應包含餐廳名稱和URL欄位
        :param use_selenium: 是否使用Selenium（推薦True，可處理JavaScript動態內容）
        """
        self.excel_file = excel_file
        self.results = []
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        
        if self.use_selenium:
            # 設定Chrome選項
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 無頭模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--single-process')  # Railway環境需要
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            try:
                # 檢查是否在Railway/Docker環境中
                import os
                import sys
                
                # 確保輸出立即刷新（Railway環境需要）
                sys.stdout.flush()
                sys.stderr.flush()
                
                chrome_binary = os.environ.get('CHROMIUM_PATH', '/usr/bin/google-chrome')
                chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', None)
                
                print("=" * 50)
                print("正在初始化Selenium...")
                print(f"CHROMIUM_PATH環境變量: {chrome_binary}")
                print(f"CHROMEDRIVER_PATH環境變量: {chromedriver_path}")
                print(f"Chrome路徑是否存在: {os.path.exists(chrome_binary) if chrome_binary else False}")
                sys.stdout.flush()
                
                # 檢查Chrome是否存在
                if os.path.exists(chrome_binary):
                    chrome_options.binary_location = chrome_binary
                    print(f"✓ 找到Chrome: {chrome_binary}")
                    
                    # 檢查Chrome版本
                    try:
                        import subprocess
                        chrome_version_output = subprocess.check_output([chrome_binary, '--version'], stderr=subprocess.STDOUT, timeout=5).decode('utf-8')
                        print(f"Chrome版本: {chrome_version_output.strip()}")
                    except Exception as e:
                        print(f"無法獲取Chrome版本: {e}")
                    
                    sys.stdout.flush()
                    
                    # 在Railway/Docker環境中，使用webdriver-manager自動下載匹配的ChromeDriver
                    # 這比手動指定路徑更可靠
                    try:
                        print("正在使用ChromeDriverManager下載ChromeDriver...")
                        sys.stdout.flush()
                        
                        # 設置ChromeDriverManager的緩存目錄（避免權限問題）
                        import tempfile
                        cache_dir = os.path.join(tempfile.gettempdir(), 'chromedriver_cache')
                        os.makedirs(cache_dir, exist_ok=True)
                        print(f"ChromeDriver緩存目錄: {cache_dir}")
                        sys.stdout.flush()
                        
                        # 使用ChromeDriverManager自動下載匹配的ChromeDriver
                        driver_path = ChromeDriverManager(cache_valid_range=365).install()
                        print(f"✓ ChromeDriver已下載: {driver_path}")
                        service = Service(driver_path)
                        sys.stdout.flush()
                    except Exception as e:
                        print(f"✗ ChromeDriverManager失敗: {e}")
                        import traceback
                        print(traceback.format_exc())
                        sys.stdout.flush()
                        
                        # 如果自動下載失敗，嘗試使用環境變量指定的路徑
                        if chromedriver_path and os.path.exists(chromedriver_path):
                            print(f"嘗試使用環境變量指定的ChromeDriver: {chromedriver_path}")
                            service = Service(chromedriver_path)
                            sys.stdout.flush()
                        else:
                            raise Exception(f"無法獲取ChromeDriver: {e}")
                else:
                    # 本地環境，嘗試自動下載
                    print(f"本地環境，使用自動下載的Chrome和ChromeDriver")
                    sys.stdout.flush()
                    service = Service(ChromeDriverManager().install())
                
                # 創建WebDriver實例
                print("正在創建Chrome WebDriver實例...")
                sys.stdout.flush()
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # 測試WebDriver是否正常工作
                self.driver.set_page_load_timeout(30)
                print("=" * 50)
                print("✓ Selenium初始化成功！已啟用（可處理JavaScript動態內容）")
                print("=" * 50)
                sys.stdout.flush()
            except Exception as e:
                print("=" * 50)
                print(f"✗ Selenium初始化失敗: {e}")
                print("=" * 50)
                import traceback
                print("完整錯誤堆棧:")
                print(traceback.format_exc())
                print("=" * 50)
                print("將使用requests（可能無法處理JavaScript動態內容）")
                print("=" * 50)
                sys.stdout.flush()
                self.use_selenium = False
                self.driver = None
        else:
            self.driver = None
        
        if not self.use_selenium:
            self.session = requests.Session()
            # 啟用連接池和keep-alive，提高性能
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10,  # 連接池大小
                pool_maxsize=20,      # 最大連接數
                max_retries=2,        # 重試次數
                pool_block=False      # 非阻塞
            )
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive'  # 保持連接
            })
    
    def __del__(self):
        """清理資源"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def load_restaurants(self):
        """從Excel載入餐廳資料"""
        try:
            df = pd.read_excel(self.excel_file)
            # 檢查必要的欄位是否存在
            if 'URL' not in df.columns:
                # 嘗試其他可能的欄位名稱
                possible_url_cols = ['網址', '網址', 'url', '連結', '連結']
                url_col = None
                for col in possible_url_cols:
                    if col in df.columns:
                        url_col = col
                        break
                if url_col:
                    df['URL'] = df[url_col]
                else:
                    raise ValueError("Excel檔案必須包含'URL'欄位（或'網址'等）")
            
            if '餐廳名稱' not in df.columns:
                # 嘗試其他可能的欄位名稱
                possible_name_cols = ['餐廳名稱', '餐厅名称', '名稱', '名称', 'name', 'Name']
                name_col = None
                for col in possible_name_cols:
                    if col in df.columns:
                        name_col = col
                        break
                if name_col:
                    df['餐廳名稱'] = df[name_col]
                else:
                    raise ValueError("Excel檔案必須包含'餐廳名稱'欄位（或'名稱'等）")
            
            return df
        except Exception as e:
            print(f"讀取Excel檔案錯誤: {e}")
            return None
    
    def check_chinese_name(self, soup):
        """檢查中文餐廳名稱"""
        # OpenRice通常使用特定的class或id來顯示中文名稱
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
                # 檢查是否包含中文字元
                if text and any('\u4e00' <= char <= '\u9fff' for char in text):
                    return True, text
        return False, None
    
    def check_english_name(self, soup):
        """檢查英文餐廳名稱"""
        # 查找英文名稱，通常在中文名稱附近或特定位置
        selectors = [
            '.pdhs-en-section',  # OpenRice特定的英文名稱類
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
                    # 檢查是否主要是英文字元（至少50%是英文字母）
                    english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
                    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
                    total_chars = len([c for c in text if c.isalnum()])
                    
                    # 必須主要是英文（英文字元數 > 中文字元數，且至少3個英文字元）
                    if total_chars > 0 and english_chars >= 3 and english_chars > chinese_chars:
                        return True, text
        
        # 檢查h1標籤中是否同時包含中英文
        h1 = soup.select_one('h1')
        if h1:
            text = h1.get_text(strip=True)
            if text:
                # 檢查英文和中文的比例
                english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
                chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
                
                # 如果英文字元數明顯多於中文字元數，且至少3個英文字元
                if english_chars >= 3 and english_chars > chinese_chars * 1.5:
                    # 提取英文部分
                    words = text.split()
                    english_words = [w for w in words if w.isalpha() and len(w) >= 2]
                    if english_words:
                        return True, ' '.join(english_words)
        
        return False, None
    
    def check_category_page(self, base_url, category_path):
        """檢查特定分類頁面是否有實際照片或影片
        category_path: 'decor', 'menu', 'food', 'videos'
        """
        try:
            # 構建分類頁面URL
            if '/photos' in base_url:
                # 如果已經是photos頁面，替換路徑
                category_url = base_url.rsplit('/photos', 1)[0] + '/photos/' + category_path
            else:
                category_url = base_url.rstrip('/') + '/photos/' + category_path
            
            soup = self.get_page_soup(category_url)
            
            # 對於videos分類，檢查是否有實際的影片
            if category_path == 'videos':
                # 檢查video標籤
                videos = soup.find_all('video')
                if len(videos) > 0:
                    return True
                
                # 檢查iframe是否有有效的影片來源
                iframes = soup.find_all('iframe')
                for iframe in iframes:
                    src = iframe.get('src', '')
                    if src and any(platform in src.lower() for platform in ['youtube', 'vimeo', 'video', 'youku', 'tiktok', 'instagram']):
                        return True
                
                # 檢查影片容器中是否有影片縮圖
                video_containers = soup.select('[class*="video"], [class*="reel"], [class*="media"]')
                video_thumbnail_count = 0
                for container in video_containers:
                    imgs = container.find_all('img')
                    for img in imgs:
                        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                        if src:
                            # 排除placeholder、logo、avatar和門面照片
                            if ('placeholder' not in src.lower() and 
                                'logo' not in src.lower() and
                                'avatar' not in src.lower() and
                                'doorphoto' not in src.lower() and  # 排除門面照片
                                ('http' in src or src.startswith('//'))):
                                # 檢查是否是OpenRice的影片相關圖片（影片CDN）
                                if ('c-vod.orstatic.com' in src or  # 影片CDN
                                    ('orstatic.com' in src and '/video/' in src.lower()) or
                                    ('orstatic.com' in src and 'reel' in src.lower())):
                                    # 進一步檢查alt屬性，排除門面照片
                                    alt = img.get('alt', '').lower()
                                    if 'door' not in alt and '門面' not in alt and '门面' not in alt:
                                        video_thumbnail_count += 1
                
                # 如果有影片縮圖，認為有影片
                if video_thumbnail_count > 0:
                    return True
                
                # 如果沒有video、有效的iframe或影片縮圖，返回False
                return False
            
            # 對於照片分類（decor, menu, food），檢查是否有實際照片
            # 檢查是否有實際的照片（不是placeholder）
            photo_list_selectors = [
                '[class*="media-list"]',
                '[class*="photo-list"]',
                '[class*="image-list"]',
                '[class*="gallery"]',
                '[class*="photo-grid"]'
            ]
            
            photo_count = 0
            
            # 方法1: 檢查照片列表容器中的圖片
            for selector in photo_list_selectors:
                containers = soup.select(selector)
                for container in containers:
                    imgs = container.find_all('img')
                    for img in imgs:
                        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                        if src:
                            # 排除placeholder圖片
                            if ('placeholder' not in src.lower() and 
                                'logo' not in src.lower() and
                                'avatar' not in src.lower() and
                                ('http' in src or src.startswith('//'))):
                                # 檢查是否是OpenRice的圖片URL
                                if ('orstatic.com' in src or 
                                    '/photo/' in src or
                                    'userphoto' in src):
                                    photo_count += 1
            
            # 方法2: 如果照片列表容器中沒有找到，檢查所有圖片
            if photo_count == 0:
                all_imgs = soup.find_all('img')
                for img in all_imgs:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                    if src:
                        # 排除placeholder和logo等非照片圖片
                        if ('placeholder' not in src.lower() and 
                            'logo' not in src.lower() and
                            'avatar' not in src.lower() and
                            ('http' in src or src.startswith('//'))):
                            # 檢查是否是使用者上傳的照片
                            if ('userphoto' in src or 
                                '/photo/' in src or
                                'orstatic.com/userphoto' in src):
                                photo_count += 1
            
            # 至少需要1張實際照片才算有照片
            return photo_count > 0
            
        except Exception as e:
            print(f"  檢查分類頁面 '/photos/{category_path}' 時出錯: {e}")
            return False
    
    def check_facade_photo(self, soup, base_url=None):
        """檢查門面照片（透過檢查 /photos/decor 頁面）"""
        if base_url:
            # 檢查 /photos/decor 頁面是否有照片
            return self.check_category_page(base_url, 'decor')
        
        # 備用方法：在主頁面查找
        img_selectors = [
            'img[class*="facade"]',
            'img[class*="exterior"]',
            'img[alt*="門面"]',
            'img[alt*="外觀"]',
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
        """檢查菜單照片（透過檢查 /menus 頁面）"""
        if base_url:
            try:
                # 構建菜單頁面URL
                if '/photos' in base_url:
                    # 如果已經是photos頁面，替換路徑
                    menu_url = base_url.rsplit('/photos', 1)[0] + '/menus'
                else:
                    menu_url = base_url.rstrip('/') + '/menus'
                
                menu_soup = self.get_page_soup(menu_url)
                
                # 先檢查是否有"沒有菜單"的提示
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
                        return False  # 明確提示沒有菜單
                
                # 檢查是否有空狀態的class或id
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
                        # 檢查這些元素中是否包含"沒有菜單"的文字
                        for elem in empty_elements:
                            elem_text = elem.get_text()
                            if any(keyword in elem_text for keyword in empty_keywords):
                                return False
                
                # 檢查是否有實際的照片（不是placeholder）
                photo_list_selectors = [
                    '[class*="media-list"]',
                    '[class*="photo-list"]',
                    '[class*="image-list"]',
                    '[class*="gallery"]',
                    '[class*="photo-grid"]'
                ]
                
                photo_count = 0
                
                # 方法1: 檢查照片列表容器中的圖片
                for selector in photo_list_selectors:
                    containers = menu_soup.select(selector)
                    for container in containers:
                        imgs = container.find_all('img')
                        for img in imgs:
                            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                            if src:
                                # 排除placeholder圖片
                                if ('placeholder' not in src.lower() and 
                                    'logo' not in src.lower() and
                                    'avatar' not in src.lower() and
                                    ('http' in src or src.startswith('//'))):
                                    # 檢查是否是OpenRice的圖片URL，排除門面照片
                                    if ('orstatic.com' in src or 
                                        '/photo/' in src or
                                        'userphoto' in src):
                                        # 排除門面照片（doorphoto）
                                        if 'doorphoto' not in src.lower():
                                            alt = img.get('alt', '').lower()
                                            if 'door' not in alt and '門面' not in alt and '门面' not in alt:
                                                photo_count += 1
                
                # 方法2: 如果照片列表容器中沒有找到，檢查所有圖片
                if photo_count == 0:
                    all_imgs = menu_soup.find_all('img')
                    for img in all_imgs:
                        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                        if src:
                            # 排除placeholder和logo等非照片圖片
                            if ('placeholder' not in src.lower() and 
                                'logo' not in src.lower() and
                                'avatar' not in src.lower() and
                                ('http' in src or src.startswith('//'))):
                                # 檢查是否是使用者上傳的照片，排除門面照片
                                if ('userphoto' in src or 
                                    '/photo/' in src or
                                    'orstatic.com/userphoto' in src):
                                    # 排除門面照片（doorphoto）
                                    if 'doorphoto' not in src.lower():
                                        alt = img.get('alt', '').lower()
                                        if 'door' not in alt and '門面' not in alt and '门面' not in alt:
                                            photo_count += 1
                
                # 至少需要1張實際照片才算有照片
                return photo_count > 0
                
            except Exception as e:
                print(f"  檢查菜單頁面 '/menus' 時出錯: {e}")
                return False
        
        # 備用方法：在主頁面查找（僅作為最後手段）
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
                    # 注意：主頁面找到菜單關鍵字不能保證有菜單照片，返回False
                    return False
        
        return False
    
    def check_food_photos(self, soup, base_url=None):
        """檢查餐點照片（透過檢查 /photos/food 頁面）"""
        if base_url:
            # 檢查 /photos/food 頁面是否有照片
            return self.check_category_page(base_url, 'food')
        
        # 備用方法：在主頁面查找
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
        
        # 如果有多個餐點照片，認為有餐點照片
        return food_photo_count >= 2
    
    def check_videos(self, soup, base_url=None):
        """檢查相關影片（透過檢查 /photos/videos 頁面）"""
        if base_url:
            # 檢查 /photos/videos 頁面是否有實際影片
            return self.check_category_page(base_url, 'videos')
        
        # 備用方法：在主頁面查找
        # 查找影片元素
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
        
        # 檢查是否有影片相關的連結
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            if any(platform in href for platform in ['youtube', 'vimeo', 'video', 'youku']):
                return True
        
        # 檢查是否有影片相關的文字
        video_keywords = ['影片', '视频', 'video', 'youtube']
        all_text = soup.get_text().lower()
        if any(keyword in all_text for keyword in video_keywords):
            # 進一步檢查是否有實際的影片元素
            if soup.find('video') or soup.find('iframe'):
                return True
        
        return False
    
    def resolve_short_url(self, url):
        """解析縮短URL，獲取實際URL
        例如: https://s.openrice.com/cHRSmW2pOW700 -> https://tw.openrice.com/zh/taichung/r-...
        """
        # 檢查是否為縮短URL
        if 's.openrice.com' in url:
            try:
                # 先嘗試HEAD請求（更輕量）
                try:
                    response = self.session.head(url, timeout=8, allow_redirects=True)
                    actual_url = response.url
                except:
                    # 如果HEAD失敗，使用GET請求
                    response = self.session.get(url, timeout=8, allow_redirects=True, stream=True)
                    actual_url = response.url
                    response.close()  # 關閉連接，不讀取內容
                
                # 移除查詢參數（如 ?_sUrl=...）
                if '?' in actual_url:
                    actual_url = actual_url.split('?')[0]
                
                # 確保URL以/結尾（如果需要的話）
                if actual_url != url:
                    print(f"  縮短URL已解析: {url} -> {actual_url}")
                
                return actual_url
            except Exception as e:
                print(f"  解析縮短URL失敗: {e}，使用原始URL")
                return url
        
        return url
    
    def get_page_soup(self, url):
        """獲取頁面的BeautifulSoup物件"""
        if self.use_selenium and self.driver:
            try:
                print(f"  使用Selenium獲取頁面: {url}")
                self.driver.get(url)
                # 等待頁面載入
                time.sleep(5)  # 增加等待時間，確保JavaScript執行完成
                # 嘗試等待特定元素載入
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    # 額外等待，確保動態內容載入
                    time.sleep(2)
                except:
                    print(f"  警告: 等待body元素超時，繼續執行")
                    time.sleep(3)  # 即使超時也等待一下
                
                html = self.driver.page_source
                page_length = len(html)
                print(f"  Selenium獲取頁面成功，內容長度: {page_length} 字元")
                
                if page_length < 1000:
                    print(f"  警告: 頁面內容可能不完整")
                
                return BeautifulSoup(html, 'html.parser')
            except Exception as e:
                print(f"  Selenium獲取頁面失敗: {e}，嘗試使用requests")
                import traceback
                print(traceback.format_exc())
                # 如果Selenium失敗，回退到requests
                pass
        
        # 使用requests作為備選
        try:
            # 減少超時時間（從15秒減少到10秒，加快失敗響應）
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 檢查Content-Encoding，如果是br (Brotli)，嘗試解壓
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            if content_encoding == 'br':
                # 嘗試使用brotli解壓
                if BROTLI_AVAILABLE:
                    try:
                        content = brotli.decompress(response.content)
                        return BeautifulSoup(content.decode('utf-8', errors='ignore'), 'html.parser')
                    except Exception as e:
                        # 如果解壓失敗，重新請求不使用br壓縮
                        pass
                
                # 如果沒有brotli庫或解壓失敗，重新請求不使用br壓縮
                headers = self.session.headers.copy()
                headers['Accept-Encoding'] = 'gzip, deflate'
                no_br_response = requests.get(url, headers=headers, timeout=10)
                no_br_response.raise_for_status()
                soup = BeautifulSoup(no_br_response.content, 'html.parser')
                
                # 檢查頁面內容是否有效
                page_text = soup.get_text() if soup else ""
                if len(page_text) < 100:
                    raise Exception(f"頁面內容過短 ({len(page_text)} 字元)，可能是JavaScript動態加載的頁面。Streamlit Cloud環境可能無法訪問OpenRice網站。")
                
                return soup
            
            # 正常情況（gzip或其他）
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 檢查頁面內容是否有效
            page_text = soup.get_text() if soup else ""
            if len(page_text) < 100:
                raise Exception(f"頁面內容過短 ({len(page_text)} 字元)，可能是JavaScript動態加載的頁面。Streamlit Cloud環境可能無法訪問OpenRice網站。")
            
            return soup
        except requests.exceptions.Timeout:
            raise Exception(f"請求超時（超過10秒），可能是網絡問題或Streamlit Cloud無法訪問OpenRice")
        except requests.exceptions.ConnectionError:
            raise Exception(f"連接錯誤，Streamlit Cloud可能無法訪問OpenRice網站")
        except Exception as e:
            raise Exception(f"無法獲取頁面: {e}")
    
    def check_restaurant(self, url, restaurant_name):
        """檢查單個餐廳的所有要素"""
        print(f"正在檢查: {restaurant_name} - {url}")
        
        try:
            # 解析縮短URL，獲取實際URL
            actual_url = self.resolve_short_url(url)
            print(f"  實際URL: {actual_url}")
            
            # 使用實際URL獲取頁面
            soup = self.get_page_soup(actual_url)
            
            # 檢查是否成功獲取頁面
            if soup is None:
                raise Exception("無法獲取頁面內容（soup為None）")
            
            # 檢查頁面是否有內容
            page_text = soup.get_text() if soup else ""
            page_text_length = len(page_text)
            print(f"  頁面內容長度: {page_text_length} 字元")
            
            # 如果頁面內容過短，可能是錯誤頁面或JavaScript未執行
            if page_text_length < 500:
                error_msg = f"頁面內容過短 ({page_text_length} 字元)，可能是：1) 網絡限制無法訪問 2) JavaScript未執行 3) 錯誤頁面"
                print(f"  錯誤: {error_msg}")
                raise Exception(error_msg)
            
            # 檢查是否包含OpenRice的關鍵字
            if 'openrice' not in page_text.lower() and 'openrice' not in actual_url.lower():
                print(f"  警告: 頁面可能不是OpenRice頁面")
            
            # 檢查是否有body標籤
            body = soup.find('body')
            if not body:
                raise Exception("頁面缺少body標籤，可能是錯誤頁面")
            
            # 使用實際URL構建子頁面URL
            checks = {
                '中文名稱': self.check_chinese_name(soup),
                '英文名稱': self.check_english_name(soup),
                '門面照片': self.check_facade_photo(soup, base_url=actual_url),
                '菜單': self.check_menu(soup, base_url=actual_url),
                '餐點照片': self.check_food_photos(soup, base_url=actual_url),
                '相關影片': self.check_videos(soup, base_url=actual_url)
            }
            
            # 打印每個檢查項目的結果（調試用）
            for key, value in checks.items():
                if isinstance(value, tuple):
                    status = "✓" if value[0] else "✗"
                    detail = value[1] if len(value) > 1 else ""
                    print(f"  {key}: {status} {detail}")
                else:
                    status = "✓" if value else "✗"
                    print(f"  {key}: {status}")
            
            # 統計通過和失敗的檢查項目
            def is_passed(check_result):
                """判斷檢查結果是否通過"""
                if isinstance(check_result, tuple):
                    return check_result[0]  # 元組的第一個元素表示是否通過
                else:
                    return bool(check_result)  # 布林值直接判斷
            
            passed = sum(1 for result in checks.values() if is_passed(result))
            total = len(checks)
            
            result = {
                '餐廳名稱': restaurant_name,
                'URL': url,
                '檢查時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '通過率': f"{passed}/{total}",
                '狀態': '合格' if passed == total else '不合格',
                **{key: ('✓' if is_passed(val) else '✗') 
                    for key, val in checks.items()}
            }
            
            return result
            
        except requests.exceptions.Timeout:
            print(f"請求超時: {restaurant_name}")
            return {
                '餐廳名稱': restaurant_name,
                'URL': url,
                '檢查時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '通過率': '0/6',
                '狀態': '錯誤',
                '錯誤資訊': '請求超時',
                '中文名稱': '✗',
                '英文名稱': '✗',
                '門面照片': '✗',
                '菜單': '✗',
                '餐點照片': '✗',
                '相關影片': '✗'
            }
        except requests.exceptions.RequestException as e:
            print(f"請求錯誤 {restaurant_name}: {e}")
            return {
                '餐廳名稱': restaurant_name,
                'URL': url,
                '檢查時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '通過率': '0/6',
                '狀態': '錯誤',
                '錯誤資訊': f'請求錯誤: {str(e)}',
                '中文名稱': '✗',
                '英文名稱': '✗',
                '門面照片': '✗',
                '菜單': '✗',
                '餐點照片': '✗',
                '相關影片': '✗'
            }
        except Exception as e:
            print(f"檢查 {restaurant_name} 時出錯: {e}")
            return {
                '餐廳名稱': restaurant_name,
                'URL': url,
                '檢查時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '通過率': '0/6',
                '狀態': '錯誤',
                '錯誤資訊': str(e),
                '中文名稱': '✗',
                '英文名稱': '✗',
                '門面照片': '✗',
                '菜單': '✗',
                '餐點照片': '✗',
                '相關影片': '✗'
            }
    
    def run_check(self, delay=1):
        """執行所有檢查"""
        df = self.load_restaurants()
        if df is None:
            return
        
        print(f"開始檢查 {len(df)} 間餐廳...")
        print("-" * 60)
        
        for idx, row in df.iterrows():
            restaurant_name = row['餐廳名稱']
            url = row['URL']
            
            # 確保URL是完整的
            if not url.startswith('http'):
                url = 'https://' + url
            
            result = self.check_restaurant(url, restaurant_name)
            self.results.append(result)
            
            # 延遲以避免請求過快
            time.sleep(delay)
            
            status_icon = '✓' if result.get('狀態') == '合格' else '✗'
            print(f"{status_icon} {restaurant_name} - {result.get('狀態', '未知')}")
        
        print("-" * 60)
        print("\n檢查完成！")
    
    def generate_report(self, output_file='restaurant_check_report.xlsx'):
        """產生檢查報告"""
        if not self.results:
            print("沒有檢查結果可產生報告")
            return
        
        df_results = pd.DataFrame(self.results)
        
        # 分離合格和不合格的餐廳
        failed_restaurants = df_results[df_results['狀態'] != '合格']
        
        # 儲存完整報告
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_results.to_excel(writer, sheet_name='完整報告', index=False)
            if len(failed_restaurants) > 0:
                failed_restaurants.to_excel(writer, sheet_name='不合格餐廳', index=False)
        
        print(f"\n報告已產生: {output_file}")
        print(f"總餐廳數: {len(df_results)}")
        print(f"合格餐廳: {len(df_results[df_results['狀態'] == '合格'])}")
        print(f"不合格餐廳: {len(failed_restaurants)}")
        
        # 列印不合格餐廳清單
        if len(failed_restaurants) > 0:
            print("\n不合格餐廳清單:")
            print("=" * 60)
            for idx, row in failed_restaurants.iterrows():
                print(f"\n{idx + 1}. {row['餐廳名稱']}")
                print(f"   URL: {row['URL']}")
                print(f"   狀態: {row['狀態']}")
                if '通過率' in row:
                    print(f"   通過率: {row['通過率']}")
                if '錯誤資訊' in row and pd.notna(row['錯誤資訊']):
                    print(f"   錯誤: {row['錯誤資訊']}")
            print("=" * 60)


def main():
    # 使用範例
    excel_file = 'restaurants.xlsx'  # 請替換為您的Excel檔案路徑
    use_selenium = True  # 設定為True使用Selenium（需要Chrome瀏覽器），False使用requests
    
    print("=" * 60)
    print("OpenRice 餐廳要素檢查程式")
    print("=" * 60)
    
    checker = OpenRiceChecker(excel_file, use_selenium=use_selenium)
    checker.run_check(delay=2 if use_selenium else 1)  # Selenium模式需要更長的延遲
    checker.generate_report('restaurant_check_report.xlsx')
    
    # 清理資源
    if checker.driver:
        checker.driver.quit()


if __name__ == '__main__':
    main()
