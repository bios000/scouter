#!/usr/bin/env python3

from typing import Set
from bs4 import BeautifulSoup
import urllib3
from .scraper import PublicDNSScraper
# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IP138Scraper(PublicDNSScraper):
    """ip138 子域名搜索"""
    
    def search(self, domain: str) -> Set[str]:
        """从 ip138 查询子域名"""
        subdomains = set()
        url = f"https://site.ip138.com/{domain}/domain.htm"
        
        try:
            response = self.session.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.select("div.panel a"):
                    subdomain = a.get_text().strip().lower()
                    if subdomain.endswith(f".{domain}"):
                        subdomains.add(subdomain)
        except Exception as e:
            print(f"[-] 从 ip138 获取数据失败: {str(e)}")
        
        return subdomains 