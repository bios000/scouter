#!/usr/bin/env python3

from typing import Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..base.scraper import BrowserScraper

class RobtexScraper(BrowserScraper):
    """Robtex 子域名搜索"""
    
    def search(self, domain: str) -> Set[str]:
        """从 Robtex 查询子域名"""
        subdomains = set()
        url = f"https://www.robtex.com/dns-lookup/{domain}"
        
        try:
            self.init_driver()
            self.driver.get(url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            
            # 查找所有链接元素
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='https://www.robtex.com/dns-lookup/']")
            for element in elements:
                href = element.get_attribute('href')
                # 从 href 中提取子域名
                subdomain = href.split('dns-lookup/')[1].strip().lower()
                if subdomain.endswith(f".{domain}"):
                    subdomains.add(subdomain)
        
        except Exception as e:
            print(f"[-] Robtex 查询失败: {str(e)}")
        
        finally:
            self.quit_driver()
        
        return subdomains 