#!/usr/bin/env python3

from typing import Set

from scouter import log_warning
from ..base.scraper import BaseScraper
from utils.colors import Colors
import requests
import time

class Quake360Scraper(BaseScraper):
    """Quake360 搜索引擎"""
    
    def __init__(self):
        super().__init__()
        self.token = self.config.get_api_key('quake360', 'api_key')
        if self.token:
            self.session.headers.update({
                'X-QuakeToken': self.token,
                'Content-Type': 'application/json'
            })
    
    def _scroll_search(self, query: str) -> Set[str]:
        """使用滚动分页搜索
        
        Args:
            query: 搜索语法
        Returns:
            Set[str]: 发现的域名集合
        """
        domains = set()
        url = "https://quake.360.net/api/v3/scroll/quake_service"
        
        # 初始请求参数
        data = {
            'query': query,
            'start': 0,
            'size': 10000,
            'ignore_cache': False,
            'shortcuts':["63734bfa9c27d4249ca7261c"]
        }
        
        pagination_id = None
        page = 1
        
        while True:
            try:
                # 添加分页ID
                if pagination_id:
                    data['pagination_id'] = pagination_id
                
                # 发送请求
                response = self.session.post(url, json=data)
                if response.status_code != 200:
                    print(self.format_log('-', Colors.error(f"请求失败，状态码: {response.status_code}"), Colors.error))
                    break
                
                result = response.json()
                
                # 提取域名
                if 'data' in result:
                    # 如果没有数据，说明到达最后一页
                    if not result['data']:
                        break
                    
                    # 处理当前页数据
                    new_domains = set()
                    for item in result['data']:
                        if 'domain' in item:
                            hostname = item['domain'].lower()
                            new_domains.add(hostname)
                    
                    if new_domains:
                        domains.update(new_domains)
                    
                    # 获取下一页的 pagination_id
                    if 'meta' in result and 'pagination_id' in result['meta']:
                        new_pagination_id = result['meta']['pagination_id']
                        if new_pagination_id == None and result['data'] == []:
                            # pagination_id 没有变化，说明到达最后一页
                            break
                        pagination_id = new_pagination_id
                        page += 1
                    else:
                        break
                else:
                    break
                
            except Exception as e:
                break
        return domains
    
    def search(self, target_domain: str) -> Set[str]:
        """从 Quake360 搜索子域名"""
        subdomains = set()
        
        if not self.token:
            log_warning("[-] 未配置 Quake360 API 密钥")
            return subdomains
        
        query = f'domain: {target_domain}'
        try:
            # 执行滚动搜索
            all_domains = self._scroll_search(query)
            
            # 过滤出目标子域名
            subdomains = {d for d in all_domains if d.endswith(f".{target_domain}")}
        except Exception as e:
            print(self.format_log('-', Colors.error(f"Quake360 搜索失败: {str(e)}"), Colors.error))
        
        return subdomains 