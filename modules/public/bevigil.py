#!/usr/bin/env python3

import os
import sys
from typing import Set

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.base.scraper import BaseScraper
from utils.colors import Colors

class BeVigilScraper(BaseScraper):
    """
    使用 BeVigil OSINT API 搜索子域名的爬虫
    
    数据源: https://osint.bevigil.com/
    """
    
    def __init__(self):
        super().__init__()
        self.source = "bevigil"
        self.base_url = "http://osint.bevigil.com/api/{}/subdomains/"
        self.api_key = self.config.get_api_key("bevigil", "api_key")
    
    def search(self, domain: str) -> Set[str]:
        """
        从 BeVigil 获取子域名
        
        Args:
            domain: 要搜索的域名
        
        Returns:
            Set[str]: 子域名集合
        """
        subdomains = set()
        
        if not self.api_key:
            print(self.format_log("!", f"{self.source} API 密钥未配置", Colors.warning))
            return subdomains
        
        try:
            # 构建请求头
            headers = {
                'X-Access-Token': self.api_key
            }
            
            # 发送请求
            response = self.get(
                self.base_url.format(domain),
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
                    
                    # 输出结果
                    if subdomains:
                        print(self.format_log("+", f"从 {self.source} 获取到 {len(subdomains)} 个子域名", Colors.success))
                    else:
                        print(self.format_log("!", f"从 {self.source} 未获取到子域名", Colors.warning))
                else:
                    print(self.format_log("-", f"从 {self.source} 获取的数据格式错误", Colors.error))
            elif response.status_code == 401:
                print(self.format_log("-", f"{self.source} API 密钥无效", Colors.error))
            elif response.status_code == 429:
                print(self.format_log("-", f"{self.source} API 请求超出限制", Colors.error))
            else:
                print(self.format_log("-", f"从 {self.source} 获取数据失败: HTTP {response.status_code}", Colors.error))
            
        except Exception as e:
            print(self.format_log("-", f"从 {self.source} 获取子域名时出错: {str(e)}", Colors.error))
        
        return subdomains
