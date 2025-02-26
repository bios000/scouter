#!/usr/bin/env python3

import requests
import json
from typing import Set
import time
import re
from utils.config import Config
from ..base.scraper import BaseScraper, BrowserScraper
from ..base.manager import DataSourceManager

class CodeScraper(BaseScraper):
    """代码仓库搜索基类"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _handle_rate_limit(self, response, min_wait=1, max_wait=5):
        """处理 API 速率限制"""
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        if remaining < 10:  # 剩余请求数较少时
            time.sleep(max_wait)
        else:
            time.sleep(min_wait)
    
    def search_code(self, domain: str) -> Set[str]:
        """搜索代码中的子域名"""
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

def get_code_subdomains(domain: str, **kwargs) -> Set[str]:
    """从多个代码仓库获取子域名"""
    manager = DataSourceManager()
    
    # 注册数据源
    from .github import GitHubScraper
    from .gitee import GiteeScraper
    
    manager.register('github', GitHubScraper)
    # manager.register('gitee', GiteeScraper)
    
    return manager.search(domain, kwargs)
