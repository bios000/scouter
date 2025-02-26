#!/usr/bin/env python3

from typing import Set
from .scraper import CTScraper

class CrtshScraper(CTScraper):
    """crt.sh 证书透明度日志搜索"""
    
    def search(self, domain: str) -> Set[str]:
        """从 crt.sh 查询子域名"""
        subdomains = set()
        query_list = [
            f"%.{domain}",
       
        ]
        for query in query_list:
            url = f"https://crt.sh/?q={query}&output=json"
            try:
                response = self.safe_request('GET', url, timeout=10, verify=False)
                if response.status_code == 200:
                    data = response.json()
                    for entry in data:
                        # 获取域名列表
                        domain_names = [name.strip() for name in entry['name_value'].split('\n')]
                        # 添加到结果集
                        subdomains.update(domain_names)
                    # 清理结果
                    subdomains = {subdomain for subdomain in subdomains if subdomain.endswith(f".{domain}")}
                    
            except Exception as e:
                print(f"[-] 从 crt.sh 获取数据失败: {str(e)}")
            
            return subdomains 