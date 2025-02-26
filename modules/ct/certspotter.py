#!/usr/bin/env python3

from typing import Set
from .scraper import CTScraper

class CertspotterScraper(CTScraper):
    """Certspotter 证书透明度日志搜索"""
    
    def search(self, domain: str) -> Set[str]:
        """从 Certspotter 查询子域名"""
        subdomains = set()
        url = f"https://api.certspotter.com/v1/issuances"
        params = {
            'domain': domain,
            'include_subdomains': 'true',
            'expand': 'dns_names'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10, verify=False)
            if response.status_code == 200:
                data = response.json()
                for cert in data:
                    if 'dns_names' in cert:
                        for dns_name in cert['dns_names']:
                            if dns_name.endswith(f".{domain}"):
                                subdomains.add(dns_name.lower())
                                
        except Exception as e:
            print(f"[-] 从 Certspotter 获取数据失败: {str(e)}")
        
        return subdomains 