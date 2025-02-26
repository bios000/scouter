#!/usr/bin/env python3

from typing import Set, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import time
from ..base.scraper import BrowserScraper
from utils.colors import Colors

class GoogleScraper(BrowserScraper):
    """Google 搜索引擎"""
    
    def __init__(self):
        super().__init__()
        # 搜索语法列表
        self.search_dorks = [
            # '*.{domain}',                              # 通配符搜索
            'site:{domain} -www',                      # 排除 www 子域名
            # 'site:{domain} (inurl:dev OR inurl:test OR inurl:staging OR inurl:admin OR inurl:api)',
            # 'site:{domain} (filetype:conf OR filetype:yaml OR filetype:env OR filetype:txt OR filetype:log OR filetype:xml OR filetype:json)',
        ]
    
    def _has_no_results(self) -> bool:
        """检查是否没有搜索结果"""
        try:
            # 检查是否存在"找不到和您查询的...相符的内容或信息"的提示
            no_results = self.driver.find_elements(By.XPATH, "//p[contains(text(), '找不到和您查询的')]")
            if no_results:
                return True
            
            # 检查是否存在"Your search did not match any documents"的提示
            no_results_en = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'did not match any documents')]")
            if no_results_en:
                return True
            
            return False
        except:
            return False
    
    def _search_with_dork(self, dork: str) -> Set[str]:
        """使用指定语法进行搜索
        
        Args:
            dork: 搜索语法
        Returns:
            Set[str]: 发现的子域名集合
        """
        subdomains = set()
        
        try:
            # 搜索
            search_input = self.wait_for_element(By.NAME, "q")
            search_input.clear()
            search_input.send_keys(dork)
            search_input.submit()
            
            # 等待页面加载
            time.sleep(2)
            
            # 检查是否有结果
            if self._has_no_results():
                print(self.format_log('!', Colors.warning(f"使用语法 {dork} 未找到结果"), Colors.warning))
                return subdomains
            
            # 等待结果
            self.wait_for_element(By.CLASS_NAME, "g")
            
            while True:
                # 提取域名
                for cite in self.driver.find_elements(By.CSS_SELECTOR, "cite.tjvcx"):
                    text = cite.text.lower()
                    if text.startswith('http'):
                        try:
                            hostname = urlparse(text).netloc
                            if hostname.endswith(f".{self.current_domain}"):
                                subdomains.add(hostname)
                        except:
                            subdomains.update(self.extract_subdomains(text, self.current_domain))
                
                # 下一页
                next_page = self.driver.find_elements(By.ID, "pnnext")
                if not next_page:
                    break
                    
                next_page[0].click()
                time.sleep(1)
                
        except Exception as e:
            print(self.format_log('-', Colors.error(f"Google 搜索失败 ({dork}): {str(e)}"), Colors.error))
        
        return subdomains
    
    def search(self, domain: str) -> Set[str]:
        """从 Google 搜索引擎查询子域名"""
        subdomains = set()
        self.current_domain = domain  # 保存当前域名供 _search_with_dork 使用
        
        try:
            self.init_driver(headless=True)
            
            # 访问 Google
            if not self.safe_get("https://www.google.com"):
                return subdomains
            
            # 使用每个搜索语法进行搜索
            for dork in self.search_dorks:
                dork = dork.format(domain=domain)
                
                # 重新访问 Google 首页
                if not self.safe_get("https://www.google.com"):
                    continue
                
                new_domains = self._search_with_dork(dork)
                if new_domains:
                    subdomains.update(new_domains)
                
                time.sleep(2)  # 避免请求过快
        except Exception as e:
            print(self.format_log('-', Colors.error(f"Google 搜索失败: {str(e)}"), Colors.error))
        
        finally:
            self.quit_driver()
        
        return subdomains 