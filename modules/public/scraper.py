#!/usr/bin/env python3

import requests
from typing import Set

from ..base.scraper import BaseScraper
from ..base.manager import DataSourceManager

class PublicDNSScraper(BaseScraper):
    """公共 DNS 数据源基类"""
    
    def __init__(self):
        super().__init__()
        
    
    def search(self, domain: str) -> Set[str]:
        """搜索子域名"""
        raise NotImplementedError("子类必须实现此方法")
    

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
    from .dnsgrep import DNSGrepScraper
    from .rapiddns import RapidDNSScraper
    from .urlscan import URLScanScraper
    # ... 注册其他数据源
    manager.register('ip138', IP138Scraper)
    manager.register('hackertarget', HackertargetScraper)
    manager.register('securitytrails', SecurityTrailsScraper)
    manager.register('dnsgrep', DNSGrepScraper)
    manager.register('netcraft', NetcraftScraper)
    manager.register('robtex', RobtexScraper)
    manager.register('dnsdumpster', DNSDumpsterScraper)
    manager.register('bevigil', BeVigilScraper)
    manager.register('rapiddns', RapidDNSScraper)
    manager.register('urlscan', URLScanScraper)
    return manager.search(domain, kwargs) 