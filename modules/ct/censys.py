#!/usr/bin/env python3

from typing import Set

from scouter import log_warning
from .scraper import CTScraper
from utils.config import Config
from utils.colors import Colors

class CensysScraper(CTScraper):
    """Censys 证书透明度日志搜索"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.api_id = self.config.get_api_key('censys', 'api_id')
        self.api_secret = self.config.get_api_key('censys', 'api_secret')
    
    def search(self, domain: str) -> Set[str]:
        """从 Censys 查询子域名"""
        subdomains = set()
        
        if not (self.api_id and self.api_secret):
            log_warning("[-] 未配置 Censys API 密钥")
            return subdomains
        
        url = "https://search.censys.io/api/v2/certificates/search"
        params = {
            'q': f'parsed.names: {domain}',
            'per_page': 100
        }
        headers = {
            'Accept': 'application/json',
        }
        auth = (self.api_id, self.api_secret)
        
        try:
            response = self.session.get(url, params=params, headers=headers, auth=auth, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'hits' in data['result']:
                    for hit in data['result']['hits']:
                        if 'parsed' in hit and 'names' in hit['parsed']:
                            for name in hit['parsed']['names']:
                                if name.endswith(f".{domain}"):
                                    subdomains.add(name.lower())
                                    
        except Exception as e:
            print(f"[-] 从 Censys 获取数据失败: {str(e)}")
        
        return subdomains 