#!/usr/bin/env python3
from typing import Set
from utils.logger import log_error, log_info, log_warning
from .scraper import IntelligenceScraper

class VirusTotalScraper(IntelligenceScraper):
    """
    使用 VirusTotal API 搜索子域名的爬虫
    
    数据源: https://www.virustotal.com/
    API 文档: https://developers.virustotal.com/reference
    """
    
    def search(self, domain: str) -> Set[str]:
        subdomains = set()
        api_key = self.config.get_api_key('virustotal', 'api_key')
        
        if not api_key:
            log_warning("VirusTotal API 密钥未配置")
            return subdomains
            
        try:
            url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains"
            headers = {'x-apikey': api_key}
            
            response = self.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    for item in data['data']:
                        if 'id' in item:
                            subdomain = item['id'].lower()
                            if subdomain.endswith(f".{domain}"):
                                subdomains.add(subdomain)
                                
        except Exception as e:
            log_error(f"VirusTotal 查询失败: {str(e)}")
            
        return subdomains 