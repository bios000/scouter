#!/usr/bin/env python3
from typing import Set

from modules.base.manager import DataSourceManager
from ..base.scraper import BaseScraper

class IntelligenceScraper(BaseScraper):
    """威胁情报平台数据源的基类"""
    def __init__(self):
        super().__init__()
        
    def search(self, domain: str) -> Set[str]:
        """搜索子域名"""
        raise NotImplementedError("子类必须实现此方法")
    
    
def get_intelligence_subdomains(domain: str, **kwargs) -> Set[str]:
    """从多个威胁情报平台获取子域名"""
    manager = DataSourceManager()
    
    from .alienvault import AlienVaultScraper
    from .threatbook import ThreatBookScraper
    from .virustotal import VirusTotalScraper
    
    manager.register('alienvault', AlienVaultScraper)
    manager.register('threatbook', ThreatBookScraper)
    manager.register('virustotal', VirusTotalScraper)
    
    return manager.search(domain, kwargs)