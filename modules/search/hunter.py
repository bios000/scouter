#!/usr/bin/env python3

from typing import Set
import requests
import base64
from utils.config import Config
from utils.logger import log_error, log_info, log_warning
from utils.colors import Colors
from ..base.scraper import BaseScraper
import time

class HunterScraper(BaseScraper):
    """奇安信鹰图 Hunter 搜索引擎"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.api_key = self.config.get_api_key('hunter', 'api_key')
        self.base_url = "https://hunter.qianxin.com/openApi/search"
    
    def _encode_search_query(self, query: str) -> str:
        """Base64 编码搜索语句"""
        return base64.urlsafe_b64encode(query.encode('utf-8')).decode('utf-8')
    
    def search(self, domain: str) -> Set[str]:
        """从 Hunter 查询子域名"""
        subdomains = set()
        
        if not self.api_key:
            log_warning("未配置 Hunter API 密钥")
            return subdomains
        
        # 构建并编码搜索语句
        search_query = f'domain.suffix="{domain}"'
        encoded_query = self._encode_search_query(search_query)
        
        # 构建查询参数
        params = {
            'api-key': self.api_key,
            'search': encoded_query,
            'page': 1,
            'page_size': 100,
            'is_web': 1
        }
        
        try:
            while True:
                # 添加重试机制
                max_retries = 3
                retry_count = 0
                
                while retry_count < max_retries:
                    response = self.session.get(self.base_url, params=params, timeout=10)
                    
                    if response.status_code != 200:
                        log_error(f"Hunter API 返回错误: {response.status_code}")
                        return subdomains
                    
                    data = response.json()

                    
                    if data.get('code') == 429:
                        retry_count += 1
                        if retry_count < max_retries:
                            log_warning(f"请求频率过高，等待后重试 ({retry_count}/{max_retries})")
                            time.sleep(5)  # 等待5秒后重试
                            continue
                        else:
                            log_error("达到最大重试次数，跳过当前页")
                            break
                    
                    if response.status_code != 200 or data.get('code') != 200:
                        log_error(f"Hunter API 返回错误: {data.get('message')}")
                        break
                    
                    # 处理响应数据
                    if 'data' in data:
                        # 检查积分额度
                        rest_quota = data['data'].get('rest_quota', '')
                        consume_quota = data['data'].get('consume_quota', '')
                        
                        # 如果剩余积分不足，终止查询
                        if '剩余积分：0' in rest_quota:
                            log_warning("Hunter API 积分已用完")
                            return subdomains
                        
                        # 处理子域名数据
                        if 'arr' in data['data']:
                            for item in data['data']['arr']:
                                if 'domain' in item:
                                    domain_name = item['domain'].lower()
                                    if domain_name.endswith(f".{domain}"):
                                        subdomains.add(domain_name)
                    
                        # 检查是否有更多页
                        total = data['data'].get('total', 0)
                        current_page = params['page']
                        total_pages = (total + params['page_size'] - 1) // params['page_size']
                        
                        if current_page >= total_pages:
                            return subdomains
                        
                        params['page'] += 1
                        break  # 成功获取数据，跳出重试循环
                
                # 如果重试次数达到上限，终止查询
                if retry_count >= max_retries:
                    break
        
        except requests.exceptions.RequestException as e:
            log_error(f"Hunter API 请求异常: {str(e)}")
        except Exception as e:
            log_error(f"处理 Hunter 数据时出错: {str(e)}")
        
        return subdomains

