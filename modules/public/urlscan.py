#!/usr/bin/env python3
from typing import Set
from utils.logger import log_error, log_info
from .scraper import PublicDNSScraper

class URLScanScraper(PublicDNSScraper):
    """
    使用 URLScan.io API 搜索子域名的爬虫
    
    数据源: https://urlscan.io/
    API 文档: https://urlscan.io/docs/api/
    """
    
    def search(self, domain: str) -> Set[str]:
        """
        从 URLScan.io 获取子域名
        
        Args:
            domain: 要搜索的域名
        
        Returns:
            Set[str]: 子域名集合
        """
        subdomains = set()
        api_key = self.config.get_api_key('urlscan', 'api_key')
        
        if not api_key:
            log_info("URLScan API 密钥未配置")
            return subdomains
            
        try:
            # 构建请求
            url = "https://urlscan.io/api/v1/search/"
            params = {
                'q': f'domain:{domain}',
                'size': 10000  # 获取最大结果数
            }
            headers = {
                'API-Key': api_key,
                'Content-Type': 'application/json'
            }
            
            # 发送请求
            response = self.get(url, params=params, headers=headers)
            
            # 解析响应
            if response.status_code == 200:
                data = response.json()
                if 'results' in data:
                    for result in data['results']:
                        # 从 page 和 task 数据中提取子域名
                        if 'page' in result:
                            domain_name = result['page'].get('domain', '')
                            if domain_name and domain_name.endswith(f".{domain}"):
                                subdomains.add(domain_name.lower())
                        
                        # 从 task 数据中提取子域名
                        if 'task' in result:
                            domain_name = result['task'].get('domain', '')
                            if domain_name and domain_name.endswith(f".{domain}"):
                                subdomains.add(domain_name.lower())
                                
        except Exception as e:
            log_error(f"URLScan 查询失败: {str(e)}")
            
        return subdomains 