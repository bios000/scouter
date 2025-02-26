#!/usr/bin/env python3

from typing import Set
from ..base.scraper import BaseScraper, BrowserScraper
from ..base.manager import DataSourceManager

class SearchEngineScraper(BrowserScraper):
    """搜索引擎基类"""
    pass

def get_search_engine_subdomains(domain: str, **kwargs) -> Set[str]:
    """从多个搜索引擎获取子域名"""
    manager = DataSourceManager()
    
    # 注册数据源
    from .google import GoogleScraper
    from .bing import BingScraper
    from .baidu import BaiduScraper
    from .quake import Quake360Scraper
    from .fofa import FofaScraper
    from .hunter import HunterScraper
    from .shodan import ShodanScraper
    
    manager.register('google', GoogleScraper)
    manager.register('bing', BingScraper)
    manager.register('baidu', BaiduScraper)
    manager.register('quake360', Quake360Scraper)
    manager.register('fofa', FofaScraper)
    manager.register('hunter', HunterScraper)
    manager.register('shodan', ShodanScraper)
    
    return manager.search(domain, kwargs) 