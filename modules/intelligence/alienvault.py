#!/usr/bin/env python3
from typing import Set
from utils.logger import log_error, log_info, log_warning
from .scraper import IntelligenceScraper

class AlienVaultScraper(IntelligenceScraper):
    """
    使用 AlienVault OTX API 搜索子域名的爬虫
    
    数据源: https://otx.alienvault.com/
    API 文档: https://otx.alienvault.com/api
    """
    
    def search(self, domain: str) -> Set[str]:
        subdomains = set()
        api_key = self.config.get_api_key('alienvault', 'api_key')
        
        if not api_key:
            log_warning("AlienVault API 密钥未配置")
            return subdomains
            
        try:
            url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
            headers = {'X-OTX-API-KEY': api_key}
            
            response = self.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'passive_dns' in data:
                    for record in data['passive_dns']:
                        hostname = record.get('hostname', '').lower()
                        if hostname and hostname.endswith(f".{domain}"):
                            subdomains.add(hostname)
                            
        except Exception as e:
            log_error(f"AlienVault 查询失败: {str(e)}")
            
        return subdomains 