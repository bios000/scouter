#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.search.scraper import get_search_engine_subdomains
def test_search_engines():
    """测试搜索引擎子域名收集功能"""
    test_domain = "qq.com"
    
    print("[*] 测试搜索引擎子域名收集功能")
    print(f"[*] 目标域名: {test_domain}")
    
    # 测试整合功能
    print("\n[*] 测试整合搜索功能...")
    try:
        all_domains = get_search_engine_subdomains(test_domain)
        if all_domains:
            print(f"[+] 搜索引擎整合测试成功，共发现 {len(all_domains)} 个子域名")
            for domain in sorted(all_domains):
                print(f"  - {domain}")
        else:
            print("[-] 搜索引擎整合测试未发现子域名")
    except Exception as e:
        print(f"[-] 搜索引擎整合测试失败: {str(e)}")

if __name__ == '__main__':
    test_search_engines() 