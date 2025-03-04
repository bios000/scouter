#!/usr/bin/env python3
from typing import Set
from bs4 import BeautifulSoup
from utils.logger import log_error, log_info
from .scraper import PublicDNSScraper

class RapidDNSScraper(PublicDNSScraper):
    """
    使用 RapidDNS 搜索子域名的爬虫
    
    数据源: https://rapiddns.io/
    """
    
    def search(self, domain: str) -> Set[str]:
        """
        从 RapidDNS 获取子域名
        
        Args:
            domain: 要搜索的域名
        
        Returns:
            Set[str]: 子域名集合
        """
        subdomains = set()
        
        try:
            # 构建请求
            url = f"https://rapiddns.io/subdomain/{domain}?full=1"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            # 发送请求
            response = self.get(url, headers=headers)
            
            # 解析响应
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找包含子域名的表格
                table = soup.find('table', {'id': 'table'})
                if table:
                    # 遍历所有行
                    for row in table.find_all('tr'):
                        # 获取第一列的子域名
                        cols = row.find_all('td')
                        if cols and len(cols) > 0:
                            subdomain = cols[0].text.strip().lower()
                            if subdomain and subdomain.endswith(f".{domain}"):
                                subdomains.add(subdomain)
                                
        except Exception as e:
            log_error(f"RapidDNS 查询失败: {str(e)}")
            
        return subdomains 