#!/usr/bin/env python3

import requests
from typing import Set
import time
import re
from modules.base.browser import BrowserBase
from ..base.scraper import BaseScraper
from ..base.manager import DataSourceManager

class CTScraper(BaseScraper):
    """证书透明度日志基类"""
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
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

def get_ct_subdomains(domain: str, **kwargs) -> Set[str]:
    """从多个 CT 日志源获取子域名"""
    manager = DataSourceManager()
    
    # 注册数据源
    from .crtsh import CrtshScraper
    from .certspotter import CertspotterScraper
    from .censys import CensysScraper
    from .crtsh import CrtshScraper
    # ... 注册其他数据源
    
    manager.register('crtsh', CrtshScraper)
    manager.register('certspotter', CertspotterScraper)
    manager.register('censys', CensysScraper)
    manager.register('crtsh', CrtshScraper)
    # ... 注册其他数据源
    
    return manager.search(domain, kwargs) 