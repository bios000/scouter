#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.ct.scraper import get_ct_subdomains

def test_ct_search():
    """测试证书透明度日志子域名收集功能"""
    test_domain = "qq.com"
    
    print("[*] 测试证书透明度日志子域名收集功能")
    print(f"[*] 目标域名: {test_domain}")
    
    try:
        subdomains = get_ct_subdomains(test_domain)
        
        if subdomains:
            print(f"\n[+] 发现 {len(subdomains)} 个子域名:")
            for subdomain in sorted(subdomains):
                print(f"    - {subdomain}")
        else:
            print("[-] 未发现子域名")
            
    except Exception as e:
        print(f"[-] 测试失败: {str(e)}")

if __name__ == '__main__':
    test_ct_search() 