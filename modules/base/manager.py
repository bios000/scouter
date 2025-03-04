#!/usr/bin/env python3

from typing import Set, Dict, Type, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from .scraper import BaseScraper
from utils.colors import Colors
from utils.logger import log_info, log_error
import time

class DataSourceManager:
    """数据源管理器，用于并发查询多个数据源"""
    
    def __init__(self, max_workers=10):
        self.sources: Dict[str, Type[BaseScraper]] = {}
        self.max_workers = max_workers
    
    def register(self, name: str, source_class: Type[BaseScraper]):
        """注册数据源"""
        self.sources[name] = source_class
    
    def search(self, domain: str, options: Dict[str, bool]) -> Set[str]:
        """并发搜索所有启用的数据源
        
        Args:
            domain: 目标域名
            options: 数据源选项，如 {'source_name': True/False}
        """
        subdomains = set()
        active_sources = []
        
        # 获取启用的数据源
        for name, enabled in options.items():
            if enabled and name in self.sources:
                active_sources.append((name, self.sources[name]))
        
        if not active_sources:
            return subdomains
            
        start_time = time.time()
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=min(len(active_sources), self.max_workers)) as executor:
            # 提交任务并记录开始
            future_to_source = {}
            for name, source_class in active_sources:
                source = source_class()
                log_info(f'正在从 {Colors.highlight(name)} {Colors.info("搜索子域名...")}')
                future_to_source[executor.submit(self._search_source, source, domain)] = (name, source)
            
            # 收集结果
            for future in as_completed(future_to_source):
                name, source = future_to_source[future]
                try:
                    result = future.result()
                    if result:
                        subdomains.update(result)
                        log_info(f'从 {Colors.highlight(name)} {Colors.info("发现")} {Colors.highlight(len(result))} {Colors.info("个子域名")}')
                except Exception as e:
                    log_error(f'从 {Colors.highlight(name)} 搜索失败: {str(e)}')
            
        return subdomains
    
    def _search_source(self, source: BaseScraper, domain: str) -> Set[str]:
        """执行单个数据源的搜索"""
        try:
            return source.search(domain)
        except Exception as e:
            log_error(f"数据源查询出错: {str(e)}")
            return set() 