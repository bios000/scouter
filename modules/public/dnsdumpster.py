#!/usr/bin/env python3

from typing import Set
from .scraper import PublicDNSScraper
import time

class DNSDumpsterScraper(PublicDNSScraper):
    """DNSDumpster 子域名搜索"""
    
    def search(self, domain: str) -> Set[str]:
        """从 DNSDumpster API 查询子域名"""
        subdomains = set()
        api_key = self.config.get_api_key('dnsdumpster', 'api_key')
        
        if not api_key:
            print("[-] 未配置 DNSDumpster API 密钥")
            return subdomains
        
        headers = {
            'X-API-Key': api_key,
            'Accept': 'application/json'
        }
        
        try:
            page = 1
            while True:
                url = f"https://api.dnsdumpster.com/domain/{domain}?page={page}"
                response = self.session.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()['a']                            
                    for record in data:
                        name = record['host'].strip().lower()
                        if name.endswith(f".{domain}"):
                            subdomains.add(name)
                    
                    page += 1  # 获取下一页
                    time.sleep(1)  # API 速率限制
                else:
                    break
                
        except Exception as e:
            print(f"[-] DNSDumpster 查询失败: {str(e)}")
        
        return subdomains 