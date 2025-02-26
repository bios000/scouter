#!/usr/bin/env python3

from typing import Set
import base64
from ..base.scraper import BaseScraper
from utils.colors import Colors

class GiteeScraper(BaseScraper):
    """Gitee 代码搜索"""
    
    def __init__(self):
        super().__init__()
        self.token = self.config.get_api_key('gitee', 'access_token')
        if self.token:
            self.session.headers.update({
                'Accept': 'application/json'
            })
    
    def search(self, domain: str) -> Set[str]:
        """从 Gitee 搜索子域名"""
        subdomains = set()
        
        if not self.token:
            print(Colors.warning("[-] 未配置 Gitee Access Token"))
            return subdomains
        
        # 搜索查询列表
        queries = [
            f'{domain}',
            f'"{domain}" language:conf',     # 配置文件
            f'"{domain}" language:yaml',     # YAML 文件
            f'"{domain}" language:html',     # HTML 文件
            f'"{domain}" language:js',       # JavaScript 文件
            f'"{domain}" language:nginx',    # Nginx 配置
            f'"{domain}" language:apache',   # Apache 配置
            f'"{domain}" path:/.well-known', # 安全文件
            f'"{domain}" path:/config',      # 配置目录
            f'"{domain}" filename:hosts',    # Hosts 文件
        ]
        
        for query in queries:
            try:
                url = "https://gitee.com/api/v5/search/repositories"
                params = {
                    'access_token': self.token,
                    'q': query,
                    'per_page': 100,
                    'page': 1
                }
                
                while True:
                    response = self.safe_request('GET', url, params=params, timeout=15)
                    if response.status_code == 200:
                        repos = response.json()
                        if not repos:  # 没有更多结果
                            break
                            
                        for repo in repos:
                            # 搜索仓库内容
                            try:
                                content_url = f"https://gitee.com/api/v5/repos/{repo['full_name']}/contents"
                                content_response = self.session.get(content_url, timeout=10)
                                if content_response.status_code == 200:
                                    files = content_response.json()
                                    for file in files:
                                        if file['type'] == 'file':
                                            # 获取文件内容
                                            download_url = file['download_url']
                                            file_response = self.session.get(download_url, timeout=10)
                                            if file_response.status_code == 200:
                                                content = file_response.text
                                                subdomains.update(self.extract_subdomains(content, domain))
                            except Exception as e:
                                print(f"[-] 获取仓库内容失败: {str(e)}")
                                continue
                        
                        params['page'] += 1  # 下一页
                        self._handle_rate_limit(response)
                        
                    elif response.status_code == 403:  # 速率限制
                        print("[!] 触发速率限制，等待重试...")
                        self._handle_rate_limit(response, max_wait=30)
                        continue
                    else:
                        print(f"[-] API 请求失败，状态码: {response.status_code}")
                        break
                    
            except Exception as e:
                print(f"[-] 搜索失败 ({query}): {str(e)}")
                continue
        
        return subdomains

def get_gitee_subdomains(domain: str) -> Set[str]:
    """从 Gitee 获取子域名"""
    scraper = GiteeScraper()
    return scraper.search(domain)
