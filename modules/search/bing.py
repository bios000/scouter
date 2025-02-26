#!/usr/bin/env python3

from typing import Set
import time
from bs4 import BeautifulSoup
import re
from .scraper import SearchEngineScraper

class BingScraper(SearchEngineScraper):
    """Bing 搜索引擎"""
    
    def search(self, domain: str) -> Set[str]:
        """从 Bing 搜索引擎查询子域名"""
        subdomains = set()
        page = 1
        
        while True:
            url = f"https://www.bing.com/search?q={domain}&first={page}"
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 提取搜索结果中的域名
                    for cite in soup.select("cite"):
                        text = cite.get_text().lower()
                        subdomains.update(self.extract_subdomains(text, domain))
                    
                    # 检查是否有下一页
                    if not soup.select("a.sb_pagN"):
                        break
                    
                    page += 10
                    time.sleep(0.5)  # 避免请求过快
                else:
                    break
                    
            except Exception as e:
                print(f"[-] Bing 搜索失败: {str(e)}")
                break
        
        return subdomains 