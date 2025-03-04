#!/usr/bin/env python3
from typing import Set

from utils.logger import log_error
from .scraper import PublicDNSScraper
from utils.colors import Colors

class BeVigilScraper(PublicDNSScraper):
    """
    使用 BeVigil OSINT API 搜索子域名的爬虫
    
    数据源: https://osint.bevigil.com/
    """
    
    def search(self, domain: str) -> Set[str]:
        """
        从 BeVigil 获取子域名
        
        Args:
            domain: 要搜索的域名
        
        Returns:
            Set[str]: 子域名集合
        """
        base_url = f"http://osint.bevigil.com/api/{domain}/subdomains/"
        subdomains = set()
        api_key = self.config.get_api_key('bevigil', 'api_key')
        
        if not api_key:
            print(self.format_log("!", f"Bevigil API 密钥未配置", Colors.warning))
            return subdomains
        
        try:
            # 构建请求头
            headers = {
                'X-Access-Token': api_key
            }
            
            # 发送请求
            response = self.get(
                base_url,
                headers=headers,
                timeout=30
            )
            
            # 解析响应
            if response and response.status_code == 200:
                data = response.json()
                if 'subdomains' in data:
                    # 提取子域名
                    for subdomain in data['subdomains']:
                        if isinstance(subdomain, str):
                            subdomain = subdomain.strip().lower()
                            if subdomain and subdomain.endswith(f".{domain}"):
                                subdomains.add(subdomain)
                    
              
        except Exception as e:
            log_error(f"Bevigil 查询失败: {str(e)}")
        
        return subdomains
