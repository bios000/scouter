#!/usr/bin/env python3

from typing import Set, Optional
import base64
from urllib.parse import urlparse
from modules.base.scraper import BaseScraper
from scouter import log_warning
from utils.colors import Colors
import time

from utils.logger import log_error

class FofaScraper(BaseScraper):
    """FOFA 搜索引擎"""
    
    def __init__(self):
        super().__init__()
        self.token = self.config.get_api_key('fofa', 'api_key')
        if self.token:
            self.session.headers.update({
                'Accept': 'application/json'
            })
        
        # 搜索语法列表
        self.search_dorks = [
            'domain="{domain}"',                                    # 证书搜索
            ]
    
    def _extract_domain(self, host: str, domain: str) -> Optional[str]:
        """从主机名或URL中提取域名"""
        host = host.lower().strip()
        
        # 如果是URL，提取主机名
        if host.startswith(('http://', 'https://')):
            try:
                host = urlparse(host).netloc
            except:
                return None
        
        # 移除端口号
        if ':' in host:
            host = host.split(':')[0]
        
        # 检查是否是目标域名的子域名
        if host.endswith(f".{domain}"):
            return host
        
        return None
    
    def search(self, domain: str) -> Set[str]:
        """从 FOFA 搜索子域名"""
        subdomains = set()
        
        if not self.token:
            log_warning("[-] 未配置 FOFA API 密钥")
            return subdomains
        
        # 使用每个搜索语法进行搜索
        for dork in self.search_dorks:
            try:
                query = dork.format(domain=domain)
                
                encoded_query = base64.b64encode(query.encode()).decode()
                params = {
                    'key': self.token,
                    'qbase64': encoded_query,
                    'size': 10000,
                    'full': False
                }
                
                response = self.safe_request('GET', "https://fofa.info/api/v1/search/all", params=params)
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data:
                        new_domains = set()
                        for result in data['results']:
                            if isinstance(result, list) and len(result) > 0:
                                host = result[0]
                                if domain_name := self._extract_domain(host, domain):
                                    new_domains.add(domain_name)
                        
                        if new_domains:
                            subdomains.update(new_domains)
                        
                time.sleep(1)  # 避免请求过快
                
            except Exception as e:
                log_error(f"FOFA 搜索失败 ({query}): {str(e)}")
                continue
        
        return subdomains