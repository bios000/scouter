#!/usr/bin/env python3

from typing import Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from utils.logger import log_error
from ..base.scraper import BrowserScraper
from utils.colors import Colors

class NetcraftScraper(BrowserScraper):
    """Netcraft 子域名搜索"""
    
    def search(self, domain: str) -> Set[str]:
        """从 Netcraft 查询子域名"""
        subdomains = set()
        base_url = "https://searchdns.netcraft.com/"
        search_url = f"{base_url}?restriction=site+contains&host=.{domain}"
        
        try:
            self.init_driver()
            
            # 访问搜索页面
            self.safe_get(search_url)
            time.sleep(3)
            
            # 检查并点击 Accept Cookies 按钮
            try:
                cookie_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn-info.teal[data-value='1']")
                if cookie_button.is_displayed():
                    cookie_button.click()
                    time.sleep(1)
            except:
                pass
            
            # 检查是否有结果
            try:
                # 等待页面加载完成
                WebDriverWait(self.driver, 10).until(
                    lambda driver: (
                        len(driver.find_elements(By.CLASS_NAME, "results-table")) > 0 or
                        len(driver.find_elements(By.CSS_SELECTOR, "h2.center")) > 0
                    )
                )
                
                # 检查是否有"无结果"消息
                no_results = self.driver.find_elements(By.CSS_SELECTOR, "h2.center")
                if no_results and "Sorry, no results were found." in no_results[0].text:
                    return subdomains
                
                # 如果有结果，继续处理
                while True:
                    # 获取当前页面的子域名
                    for element in self.driver.find_elements(By.CLASS_NAME, "results-table__host"):
                        subdomain = element.text.strip().lower()
                        if subdomain.endswith(f".{domain}"):
                            subdomains.add(subdomain)
                    
                    # 检查是否有下一页
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, "a[class='btn-info']")
                        if not next_button.is_enabled():
                            break
                        
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(0.5)
                        
                        self.driver.execute_script("arguments[0].click();", next_button)
                        
                        WebDriverWait(self.driver, 10).until(
                            EC.staleness_of(next_button)
                        )
                    except:
                        break
                
            except Exception as e:
                log_error(f"Netcraft 搜索失败: {str(e)}")
                return subdomains
        
        finally:
            self.quit_driver()
        
        return subdomains 