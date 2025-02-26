#!/usr/bin/env python3

import requests
from typing import Set
import time
import re
import urllib3
from utils.colors import Colors
from utils.config import Config
from modules.base.browser import BrowserBase
from datetime import datetime
from utils.retry import retry_on_error

# 禁用所有 SSL 警告
urllib3.disable_warnings()

class BaseScraper:
    """所有数据源的基类"""
    
    @staticmethod
    def get_timestamp() -> str:
        """获取当前时间戳"""
        return datetime.now().strftime('%H:%M:%S')
    
    @staticmethod
    def format_log(symbol: str, message: str, color_func=None) -> str:
        """格式化日志消息
        
        Args:
            symbol: 消息符号 (+, -, *, !)
            message: 消息内容
            color_func: 颜色函数
        """
        timestamp = BaseScraper.get_timestamp()
        if color_func:
            return f"[{Colors.info(timestamp)}][{color_func(symbol)}] {message}"
        return f"[{timestamp}][{symbol}] {message}"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.verify = False  # 统一禁用 SSL 验证
        self.config = Config()
    
    def search(self, domain: str) -> Set[str]:
        """搜索子域名"""
        raise NotImplementedError("子类必须实现此方法")
    
    def extract_subdomains(self, content: str, domain: str) -> Set[str]:
        """从文本中提取子域名"""
        subdomains = set()
        pattern = r'[a-zA-Z0-9][-a-zA-Z0-9]*\.' + re.escape(domain)
        matches = re.finditer(pattern, content)
        for match in matches:
            subdomain = match.group(0).lower()
            if subdomain.endswith(f".{domain}"):
                subdomains.add(subdomain)
        return subdomains
    
    def _handle_rate_limit(self, response, min_wait=1, max_wait=5):
        """处理 API 速率限制"""
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        if remaining < 10:  # 剩余请求数较少时
            time.sleep(max_wait)
        else:
            time.sleep(min_wait)

    @retry_on_error(max_retries=3, delay=1)
    def safe_request(self, method, url, **kwargs):
        """安全的请求方法，带有重试机制"""
        kwargs.setdefault('timeout', 10)  # 默认超时时间
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()  # 抛出非 200 状态码的异常
        return response
    
    def get(self, url, **kwargs):
        """GET 请求"""
        return self.safe_request('GET', url, **kwargs)
    
    def post(self, url, **kwargs):
        """POST 请求"""
        return self.safe_request('POST', url, **kwargs)

class BrowserScraper(BaseScraper, BrowserBase):
    """需要浏览器功能的数据源基类"""
    
    def __init__(self):
        BaseScraper.__init__(self)
        BrowserBase.__init__(self) 