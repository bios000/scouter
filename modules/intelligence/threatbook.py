#!/usr/bin/env python3
from typing import Set
from utils.logger import log_error, log_info, log_warning
from .scraper import IntelligenceScraper

class ThreatBookScraper(IntelligenceScraper):
    """
    使用微步在线 API 搜索子域名的爬虫
    
    数据源: https://x.threatbook.com/
    API 文档: https://x.threatbook.com/v5/api
    """
    
    def search(self, domain: str) -> Set[str]:
        subdomains = set()
        api_key = self.config.get_api_key('threatbook', 'api_key')
        
        if not api_key:
            log_warning("微步在线 API 密钥未配置")
            return subdomains
            
        try:
            url = "https://api.threatbook.cn/v3/domain/sub_domains"
            params = {
                'apikey': api_key,
                'resource': domain
            }
            
            response = self.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('response_code') == 0:
                    sub_domains = data.get('sub_domains', [])
                    for subdomain in sub_domains:
                        if subdomain.endswith(f".{domain}"):
                            subdomains.add(subdomain.lower())
                            
        except Exception as e:
            log_error(f"微步在线查询失败: {str(e)}")
            
        return subdomains 