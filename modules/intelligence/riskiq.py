#!/usr/bin/env python3
from typing import Set
from utils.logger import log_error, log_info
from .scraper import IntelligenceScraper
import base64

class RiskIQScraper(IntelligenceScraper):
    """
    使用 RiskIQ PassiveTotal API 搜索子域名的爬虫
    
    数据源: https://community.riskiq.com/
    API 文档: https://api.passivetotal.org/api/docs/
    """
    
    def search(self, domain: str) -> Set[str]:
        subdomains = set()
        api_key = self.config.get_api_key('riskiq', 'api_key')
        api_secret = self.config.get_api_key('riskiq', 'api_secret')
        
        if not (api_key and api_secret):
            log_info("RiskIQ API 密钥未配置")
            return subdomains
            
        try:
            url = f"https://api.passivetotal.org/v2/enrichment/subdomains"
            auth = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/json'
            }
            params = {'query': domain}
            
            response = self.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'subdomains' in data:
                    for subdomain in data['subdomains']:
                        full_domain = f"{subdomain}.{domain}".lower()
                        subdomains.add(full_domain)
                            
        except Exception as e:
            log_error(f"RiskIQ 查询失败: {str(e)}")
            
        return subdomains 