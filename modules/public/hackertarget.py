#!/usr/bin/env python3

from typing import Set

import urllib3
from .scraper import PublicDNSScraper
# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HackertargetScraper(PublicDNSScraper):
    """Hackertarget 子域名搜索"""
    
    def search(self, domain: str) -> Set[str]:
        """从 hackertarget 查询子域名"""
        subdomains = set()
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        
        try:
            response = self.session.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                lines = response.text.splitlines()
                for line in lines:
                    if ',' in line:
                        subdomain = line.split(',')[0].strip().lower()
                        if subdomain.endswith(f".{domain}"):
                            subdomains.add(subdomain)
        except Exception as e:
            print(f"[-] 从 hackertarget 获取数据失败: {str(e)}")
        
        return subdomains 