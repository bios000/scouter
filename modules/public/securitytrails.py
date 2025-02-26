#!/usr/bin/env python3

from typing import Set
from .scraper import PublicDNSScraper
from utils.colors import Colors

class SecurityTrailsScraper(PublicDNSScraper):
    """SecurityTrails 子域名搜索"""
    
    def __init__(self):
        super().__init__()
        self.api_key = self.config.get_api_key('securitytrails', 'api_key')
    
    def search(self, domain: str) -> Set[str]:
        """从 SecurityTrails 查询子域名"""
        subdomains = set()
        
        if not self.api_key:
            print(Colors.warning("[-] 未配置 SecurityTrails API 密钥"))
            return subdomains
            
        url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
        headers = {
            'APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'subdomains' in data:
                    for subdomain in data['subdomains']:
                        full_domain = f"{subdomain}.{domain}".lower()
                        subdomains.add(full_domain)
        except Exception as e:
            print(Colors.error(f"[-] 从 SecurityTrails 获取数据失败: {str(e)}"))
        
        return subdomains 