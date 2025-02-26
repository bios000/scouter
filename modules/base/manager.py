#!/usr/bin/env python3

from typing import Set, Dict, Type
from .scraper import BaseScraper
from utils.colors import Colors

class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self):
        self.sources: Dict[str, Type[BaseScraper]] = {}
    
    def register(self, name: str, scraper_class: Type[BaseScraper]):
        """注册数据源"""
        self.sources[name] = scraper_class
    
    def search(self, domain: str, sources: Dict[str, bool] = None) -> Set[str]:
        """从指定的数据源搜索子域名"""
        all_subdomains = set()
        
        # 如果没有指定数据源，使用所有已注册的数据源
        if sources is None:
            sources = {name: True for name in self.sources}
        
        for name, enabled in sources.items():
            if enabled and name in self.sources:
                try:
                    scraper = self.sources[name]()
                    print(scraper.format_log(
                        '*',
                        f"{Colors.success('正在从')} {Colors.highlight(name)} {Colors.success('搜索子域名...')}",
                        Colors.info
                    ))
                    
                    subdomains = scraper.search(domain)
                    print(scraper.format_log(
                        '+',
                        f"{Colors.success('从')} {Colors.highlight(name)} {Colors.success('发现')} {Colors.BRIGHT_WHITE}{len(subdomains)}{Colors.success(' 个子域名')}",
                        Colors.success
                    ))
                    
                    if subdomains:
                        all_subdomains.update(subdomains)
                except Exception as e:
                    print(scraper.format_log(
                        '-',
                        f"{Colors.error('从')} {Colors.highlight(name)} {Colors.error(f'搜索失败: {str(e)}')}",
                        Colors.error
                    ))
        
        return all_subdomains 