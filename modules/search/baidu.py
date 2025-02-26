#!/usr/bin/env python3

from typing import Set
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .scraper import SearchEngineScraper
from utils.colors import Colors

class BaiduScraper(SearchEngineScraper):
    """百度搜索引擎"""
    
    def _is_last_page(self) -> bool:
        """检查是否是最后一页"""
        try:
            # 检查是否存在下一页按钮
            next_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), '下一页')]")
            if not next_buttons:
                return True
            
            # 检查下一页按钮是否可用
            next_page = next_buttons[0]
            return not (next_page.is_displayed() and next_page.is_enabled())
        except:
            return True
    
    def search(self, domain: str) -> Set[str]:
        """从百度搜索引擎查询子域名"""
        subdomains = set()
        
        try:
            self.init_driver()
            
            # 访问百度首页
            self.safe_get("https://www.baidu.com")
            time.sleep(1)
            
            # 搜索
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "kw"))
            )
            search_input.clear()
            search_input.send_keys(f"site:{domain}")
            
            # 点击搜索
            search_button = self.driver.find_element(By.ID, "su")
            search_button.click()
            
            # 等待结果
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )
            
            page_num = 1
            max_pages = 100  # 最多爬取50页
            max_retries = 3  # 每页最多重试3次
            
            while page_num <= max_pages:
                # 检查验证码
                if '安全验证' in self.driver.page_source:
                    print(self.format_log('-', Colors.warning("百度搜索遇到验证码"), Colors.warning))
                    break
                
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        # 提取域名
                        results = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.result.c-container.xpath-log.new-pmd"))
                        )
                        
                        for result in results:
                            try:
                                # 从 mu 属性中提取 URL
                                mu = result.get_attribute('mu')
                                if mu:
                                    subdomains.update(self.extract_subdomains(mu.lower(), domain))
                                
                                # 从文本内容中提取域名
                                text = result.text.lower()
                                subdomains.update(self.extract_subdomains(text, domain))
                            except:
                                continue
                        
                        # 检查是否是最后一页
                        if self._is_last_page():
                            # print(self.format_log('*', Colors.success(f"已到达最后一页（第 {page_num} 页），完成爬取"), Colors.success))
                            return subdomains
                        
                        # 查找并点击下一页按钮
                        next_page = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '下一页')]"))
                        )
                        
                        # 滚动到按钮位置
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
                        
                        # 点击下一页
                        next_page.click()
                        
                        # 等待新页面加载
                        WebDriverWait(self.driver, 10).until(
                            lambda driver: driver.find_elements(By.CSS_SELECTOR, "div.result.c-container.xpath-log.new-pmd")
                        )
                        
                        page_num += 1
                        time.sleep(1)
                        break  # 成功后跳出重试循环
                        
                    except Exception as e:
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(1)
                            # 刷新当前页面
                            self.driver.refresh()
                            time.sleep(1)
                            continue
                        else:
                            return subdomains
        
        except Exception as e:
            print(self.format_log('-', Colors.error(f"百度搜索失败: {str(e)}"), Colors.error))
        
        finally:
            self.quit_driver()
        
        return subdomains 