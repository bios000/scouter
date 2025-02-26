#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import random
import time
from utils.config import Config
from utils.retry import retry_on_error

class BrowserBase:
    """浏览器基类，提供通用的 Selenium 功能"""
    
    def __init__(self):
        self.config = Config()
        self.driver = None
    
    def init_driver(self, headless=True):
        """初始化 WebDriver
        
        Args:
            headless: 是否使用无头模式
        """
        if self.driver is None:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            
            # 基本配置
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--incognito')  # 无痕模式
            
            # 随机 User-Agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
            chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # 实验性选项
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 代理配置
            proxy = self.config.get_api_key('proxy')
            if proxy:
                if proxy.get('socks'):
                    chrome_options.add_argument(f'--proxy-server={proxy["socks"]}')
                elif proxy.get('http'):
                    chrome_options.add_argument(f'--proxy-server={proxy["http"]}')
                elif proxy.get('https'):
                    chrome_options.add_argument(f'--proxy-server={proxy["https"]}')
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # 修改 WebDriver 属性
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    '''
                })
                
                # 设置页面加载超时
                self.driver.set_page_load_timeout(30)
                
            except Exception as e:
                print(f"[-] Chrome WebDriver 初始化失败: {str(e)}")
                if self.driver:
                    self.quit_driver()
                raise e
    
    def quit_driver(self):
        """关闭 WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None
    
    def wait_for_element(self, by, value, timeout=10):
        """等待元素出现
        
        Args:
            by: 定位方式 (By.ID, By.CLASS_NAME 等)
            value: 定位值
            timeout: 超时时间(秒)
        Returns:
            找到的元素
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_elements(self, by, value, timeout=10):
        """等待多个元素出现"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
    
    @retry_on_error(max_retries=3, delay=1)
    def safe_get(self, url):
        """安全的页面访问方法"""
        self.driver.get(url)
        return True
    
    @retry_on_error(max_retries=3, delay=1)
    def safe_find_element(self, by, value):
        """安全的元素查找方法"""
        return self.driver.find_element(by, value)
    
    def check_captcha(self, keywords=('验证码', 'captcha', 'verify')):
        """检查是否存在验证码
        
        Args:
            keywords: 验证码关键词
        Returns:
            bool: 是否存在验证码
        """
        page_source = self.driver.page_source.lower()
        return any(keyword.lower() in page_source for keyword in keywords)
    
    def __enter__(self):
        """上下文管理器入口"""
        self.init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.quit_driver() 