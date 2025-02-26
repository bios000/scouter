#!/usr/bin/env python3

import requests
from typing import Set
import time
import re
from modules.base.browser import BrowserBase
from utils.config import Config
from ..base.scraper import BaseScraper
from ..base.manager import DataSourceManager

class PublicDNSScraper(BaseScraper):
    """公共 DNS 数据源基类"""
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
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

def get_public_dns_subdomains(domain: str, **kwargs) -> Set[str]:
    """从多个公共 DNS 数据源获取子域名"""
    manager = DataSourceManager()
    
    # 注册数据源
    from .ip138 import IP138Scraper
    from .hackertarget import HackertargetScraper
    from .securitytrails import SecurityTrailsScraper
    from .netcraft import NetcraftScraper
    from .robtex import RobtexScraper
    from .dnsdumpster import DNSDumpsterScraper
    from .bevigil import BeVigilScraper
    
    # ... 注册其他数据源
    manager.register('ip138', IP138Scraper)
    manager.register('hackertarget', HackertargetScraper)
    manager.register('securitytrails', SecurityTrailsScraper)
    manager.register('netcraft', NetcraftScraper)
    manager.register('robtex', RobtexScraper)
    manager.register('dnsdumpster', DNSDumpsterScraper)
    manager.register('bevigil', BeVigilScraper)
    
    return manager.search(domain, kwargs) 