#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.code.scraper import get_code_subdomains
from utils.config import Config
from utils.colors import Colors

def test_github_search():
    """测试 GitHub 子域名搜集功能"""
    # 测试域名
    test_domain = "58corp.com"
    
    print(f"[{Colors.info('*')}] {Colors.success('测试 GitHub 子域名搜集功能')}")
    print(f"[{Colors.info('*')}] {Colors.success('目标域名:')} {Colors.highlight(test_domain)}")
    
    # 检查配置
    config = Config()
    github_token = config.get_api_key('github')
    
    if not github_token:
        print(Colors.warning("[-] 未配置 GitHub Token，请先配置:"))
        print(Colors.dim("    python scouter.py config --set github:your_token_here"))
        return
    
    try:
        # 执行搜索
        subdomains = get_code_subdomains(test_domain, github=True, gitee=False)
        
        # 打印结果
        if subdomains:
            print(f"\n[{Colors.success('+')}] {Colors.success('发现')} {Colors.BRIGHT_WHITE}{len(subdomains)}{Colors.success(' 个子域名:')}")
            
            # 打印子域名列表
            print(Colors.BLUE + "=" * 60)
            for subdomain in sorted(subdomains):
                print(f"    {Colors.highlight(subdomain)}")
            print(Colors.BLUE + "=" * 60 + Colors.RESET)
        else:
            print(Colors.warning("[-] 未发现子域名"))
            
    except Exception as e:
        print(Colors.error(f"[-] 测试失败: {str(e)}"))

if __name__ == '__main__':
    test_github_search() 