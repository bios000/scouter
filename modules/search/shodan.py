#!/usr/bin/env python3

from typing import Set
import requests
from utils.config import Config
from utils.logger import log_error, log_info, log_warning
from utils.colors import Colors
from ..base.scraper import BaseScraper
import time

class ShodanScraper(BaseScraper):
    """Shodan 搜索引擎"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.api_key = self.config.get_api_key('shodan', 'api_key')
        
    
    def search(self, domain: str) -> Set[str]:
        """从 Shodan 查询子域名"""
        log_info(f"正在从 Shodan 搜索子域名: {domain}")
        subdomains = set()
        
        if not self.api_key:
            log_warning("未配置 Shodan API 密钥")
            return subdomains
        
        self.base_url =f"https://api.shodan.io/dns/domain/{domain}"
        
        # 构建查询参数
        params = {
            'key': self.api_key,
        }
        
        try:
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                response = self.session.get(self.base_url, params=params, timeout=10)
                
                # 处理速率限制
                if response.status_code == 429:
                    retry_count += 1
                    if retry_count < max_retries:
                        log_warning(f"请求频率过高，等待后重试 ({retry_count}/{max_retries})")
                        time.sleep(5)  # 等待5秒后重试
                        continue
                    else:
                        log_error("达到最大重试次数，终止查询")
                        break
                
                # 处理其他错误
                if response.status_code != 200:
                    log_error(f"Shodan API 请求失败: HTTP {response.status_code}")
                    break
                
                try:
                    data = response.json()
                   
                    # 处理域名数据
                    if 'subdomains' in data:
                        for subdomain in data['subdomains']:
                            full_domain = f"{subdomain}.{domain}".lower()
                            subdomains.add(full_domain)
                    
                    # Shodan 的子域名 API 不需要分页
                    break
                    
                except ValueError as e:
                    log_error(f"解析 Shodan 响应失败: {str(e)}")
                    break
        
        except requests.exceptions.RequestException as e:
            log_error(f"Shodan API 请求异常: {str(e)}")
        except Exception as e:
            log_error(f"处理 Shodan 数据时出错: {str(e)}")
        
        return subdomains 