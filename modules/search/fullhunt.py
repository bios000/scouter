#!/usr/bin/env python3
from typing import Set
from utils.logger import log_error, log_info
from .scraper import SearchEngineScraper

class FullHuntScraper(SearchEngineScraper):
    """
    使用 FullHunt API 搜索子域名的爬虫
    
    数据源: https://fullhunt.io/
    """
    
    def search(self, domain: str) -> Set[str]:
        """
        从 FullHunt 获取子域名
        
        Args:
            domain: 要搜索的域名
        
        Returns:
            Set[str]: 子域名集合
        """
        subdomains = set()
        api_key = self.config.get_api_key('fullhunt', 'api_key')
        
        if not api_key:
            log_info("FullHunt API 密钥未配置")
            return subdomains
            
        try:
            # 构建请求
            url = f"https://fullhunt.io/api/v1/domain/{domain}/subdomains"
            headers = {
                'X-API-KEY': api_key,
                'Accept': 'application/json'
            }
            
            # 发送请求
            response = self.get(url, headers=headers)
            
            # 解析响应
            if response.status_code == 200:
                data = response.json()
                if 'hosts' in data:
                    for subdomain in data['hosts']:
                        if isinstance(subdomain, str):
                            subdomain = subdomain.strip().lower()
                            if subdomain and subdomain.endswith(f".{domain}"):
                                subdomains.add(subdomain)
                                
        except Exception as e:
            log_error(f"FullHunt 查询失败: {str(e)}")
            
        return subdomains 