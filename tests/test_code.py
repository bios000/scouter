#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.code.scraper import get_code_subdomains
from utils.config import Config

def test_code_search():
    """测试代码仓库子域名搜集功能"""
    test_domain = "58.com"
    
    print("[*] 测试代码仓库子域名搜集功能")
    print(f"[*] 目标域名: {test_domain}")
    
    # 检查配置
    config = Config()
    github_token = config.get_api_key('github')
    gitee_token = config.get_api_key('gitee', 'access_token')
    
    if not github_token and not gitee_token:
        print("[-] 未配置任何代码仓库 Token，请先配置:")
        print("    python scouter.py config")
        return
    
    try:
        subdomains = get_code_subdomains(test_domain)
        
        if subdomains:
            print(f"\n[+] 发现 {len(subdomains)} 个子域名:")
            for subdomain in sorted(subdomains):
                print(f"    - {subdomain}")
        else:
            print("[-] 未发现子域名")
            
    except Exception as e:
        print(f"[-] 测试失败: {str(e)}")

if __name__ == '__main__':
    test_code_search() 