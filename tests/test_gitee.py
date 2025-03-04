#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.code.gitee import get_gitee_subdomains
from utils.config import Config

def test_gitee_search():
    """测试 Gitee 子域名搜集功能"""
    test_domain = "58.com"
    
    print("[*] 测试 Gitee 子域名搜集功能")
    print(f"[*] 目标域名: {test_domain}")
    
    # 检查配置
    config = Config()
    gitee_token = config.get_api_key('gitee', 'access_token')
    
    gitee_token = "39e2f679d94325b7d2162711dba0b680"
    if not gitee_token:
        print("[-] 未配置 Gitee Token，请先配置:")
        print("    python scouter.py config --set gitee:access_token:your_token_here")
        return
    
    try:
        subdomains = get_gitee_subdomains(test_domain)
        
        if subdomains:
            print(f"\n[+] 发现 {len(subdomains)} 个子域名:")
            for subdomain in sorted(subdomains):
                print(f"    - {subdomain}")
        else:
            print("[-] 未发现子域名")
            
    except Exception as e:
        print(f"[-] 测试失败: {str(e)}")

if __name__ == '__main__':
    test_gitee_search() 