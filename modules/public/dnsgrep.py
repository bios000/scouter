#!/usr/bin/env python3

import os
import sys
from typing import Set
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from .scraper import PublicDNSScraper
from utils.logger import log_info, log_error, log_success, log_warning
from utils.CloudflareBypasser import CloudflareBypass


# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class DNSGrepScraper(PublicDNSScraper):
    """
    使用 DNSGrep 搜索子域名的爬虫
    
    数据源: https://www.dnsgrep.cn/
    """
        
    def search(self, domain: str) -> Set[str]:
        """
        从 DNSGrep 获取子域名
        
        Args:
            domain: 要搜索的域名
        
        Returns:
            Set[str]: 子域名集合
        """
        subdomains = set()
        
        try:
            browser_path  = r'/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
            url = f'https://www.dnsgrep.cn/subdomain/{domain}'
            cf = CloudflareBypass(browser_path, url)
            user_agent,cookies = cf.bypass()
            headers = {
                'User-Agent': user_agent,
                'Cookie': cookies
            }
            response = self.session.get(url, headers=headers,verify=False)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找所有包含子域名的 td 元素
            for td in soup.find_all('td', attrs={'data': True}):
                subdomain = td.get('data').strip().lower()
                if subdomain and subdomain.endswith(f".{domain}"):
                    subdomains.add(subdomain)
                    
        except Exception as e:
            log_error(f"从 DNSGrep 获取 {domain} 的子域名失败: {str(e)}")
            
        return subdomains 