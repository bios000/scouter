#!/usr/bin/env python3

import requests
import json
from typing import Set
import time
import re
import base64
from utils.config import Config
from .scraper import CodeScraper
from ..base.scraper import BaseScraper
from utils.colors import Colors

class GitHubScraper(BaseScraper):
    """GitHub 代码搜索"""
    
    def __init__(self):
        super().__init__()
        self.token = self.config.get_api_key('github','api_key')
        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github+json'
            })
    
    def _handle_rate_limit(self, response):
        """处理 API 速率限制"""
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        limit = int(response.headers.get('X-RateLimit-Limit', 0))
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        
        # 如果剩余请求数小于总限制的 10%，则进行等待
        if remaining < limit * 0.1:
            wait_time = reset_time - int(time.time())
            if wait_time > 0:
                print(f"[*] API 剩余请求数: {remaining}/{limit}")
                print(f"[*] 等待 {wait_time} 秒后继续...")
                time.sleep(min(wait_time, 30))  # 最多等待 30 秒
        elif remaining < limit * 0.2:
            # 剩余请求数较少时，增加请求间隔
            time.sleep(5)
        else:
            # 正常请求间隔
            time.sleep(1)

    def search(self, domain: str) -> Set[str]:
        """从 GitHub 搜索子域名"""
        subdomains = set()
        
        if not self.token:
            print(self.format_log('-', Colors.warning("未配置 GitHub API Token"), Colors.warning))
            return subdomains
        
        # 搜索代码
        code_domains = self._search_code(domain)
        if code_domains:
            # print(self.format_log(
            #     '+',
            #     f"{Colors.success('从 GitHub 代码中发现')} {Colors.BRIGHT_WHITE}{len(code_domains)}{Colors.success(' 个子域名')}",
            #     Colors.success
            # ))
            subdomains.update(code_domains)
        # else:
        #     print(self.format_log('*', Colors.info("GitHub 代码搜索未发现子域名"), Colors.info))
        
        # 搜索 Issues
        issue_domains = self._search_issues(domain)
        if issue_domains:
            # print(Colors.success(f"[+] 从 GitHub Issues 中发现 {len(issue_domains)} 个子域名"))
            subdomains.update(issue_domains)
        # else:
        #     print(Colors.info(f"[*] GitHub Issues 搜索未发现子域名"))
        
        return subdomains
    
    def _search_code(self, domain: str) -> Set[str]:
        """搜索 GitHub 代码中的子域名"""
        subdomains = set()
        
        if not self.token:
            print(Colors.warning("[-] 未配置 GitHub API Token"))
            return subdomains
        
        # 搜索查询列表
        queries = [
            f'"{domain}"',
        #     f'"{domain}" path:/.well-known/security.txt',  # 安全文件
        #     f'"{domain}" filename:cname',                  # CNAME 文件
        #     f'"{domain}" filename:config',                 # 配置文件
        #     f'"{domain}" filename:*.html',                 # HTML 文件
        #     f'"{domain}" filename:*.js',                   # JavaScript 文件
        #     f'"{domain}" filename:*.txt',                  # 文本文件
        #     f'"{domain}" filename:*.conf',                 # 配置文件
        #     f'"{domain}" filename:*.yml',                  # YAML 文件
        #     f'"{domain}" filename:*.yaml',                 # YAML 文件
        #     f'"{domain}" filename:*.xml',                  # XML 文件
        #     f'"{domain}" filename:*.json',                 # JSON 文件
        #     f'"{domain}" filename:*.env',                  # 环境配置文件
        #     f'"{domain}" filename:nginx*',                 # Nginx 配置
        #     f'"{domain}" filename:apache*',                # Apache 配置
        #     f'"{domain}" filename:hosts',                  # Hosts 文件
        ]
        
        for query in queries:
            try:
                url = "https://api.github.com/search/code"
                params = {
                    'q': query,
                    'per_page': 100
                }
                
                response = self.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if 'items' in data:
                        for item in data['items']:
                            if 'url' in item:
                                try:
                                    content_response = self.session.get(item['url'], timeout=10)
                                    if content_response.status_code == 200:
                                        content_data = content_response.json()
                                        if 'content' in content_data:
                                            content = base64.b64decode(content_data['content']).decode('utf-8', errors='ignore')
                                            
                                            # 使用正则表达式查找子域名
                                            pattern = r'[a-zA-Z0-9][-a-zA-Z0-9]*\.' + re.escape(domain)
                                            matches = re.finditer(pattern, content)
                                            for match in matches:
                                                subdomain = match.group(0).lower()
                                                if subdomain.endswith(f".{domain}"):
                                                    subdomains.add(subdomain)
                                except Exception as e:
                                    print(Colors.error(f"[-] 获取文件内容失败: {str(e)}"))
                                    continue
                elif response.status_code == 403:  # 速率限制
                    print("[!] 触发速率限制，等待重试...")
                    self._handle_rate_limit(response)
                    continue
                
                # 处理速率限制
                self._handle_rate_limit(response)
                
            except Exception as e:
                print(Colors.error(f"[-] 搜索失败 ({query}): {str(e)}"))
                continue
        
        return subdomains
    
    def _search_issues(self, domain: str) -> Set[str]:
        """搜索 GitHub Issues 中的子域名"""
        subdomains = set()
        
        if not self.token:
            return subdomains
        
        try:
            url = "https://api.github.com/search/issues"
            params = {
                'q': f'"{domain}" in:body,title,comments',
                'per_page': 100
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'items' in data:
                    for item in data['items']:
                        # 搜索 issue 标题和内容
                        content = f"{item.get('title', '')} {item.get('body', '')}"
                        pattern = r'[a-zA-Z0-9][-a-zA-Z0-9]*\.' + re.escape(domain)
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            subdomain = match.group(0).lower()
                            if subdomain.endswith(f".{domain}"):
                                subdomains.add(subdomain)
            
            time.sleep(2)
            
        except Exception as e:
            print(Colors.error(f"[-] Issues 搜索失败: {str(e)}"))
        
        return subdomains

