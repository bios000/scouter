#!/usr/bin/env python3

from modules.public.scraper import PublicDNSScraper
import sys

def test_public_dns_search(target_domain):
    """测试公开 DNS 记录查询功能"""
    print(f"\n[*] 开始测试公开 DNS 记录查询功能")
    print(f"[*] 目标域名: {target_domain}")
    print("=" * 60)
    
    # 创建 PublicDNSScraper 实例
    scraper = PublicDNSScraper()
    
    # 定义所有数据源及其测试函数
    sources = [
        ('ip138', scraper.search_ip138),
        ('hackertarget', scraper.search_hackertarget),
        ('SecurityTrails', scraper.search_securitytrails),
        ('Netcraft', scraper.search_netcraft)
    ]
    
    # 测试每个数据源
    total_domains = set()
    for source_name, search_func in sources:
        try:
            domains = search_func(target_domain)
            if domains:
                total_domains.update(domains)
                print(f"[+] {source_name:<15} 发现 {len(domains):>3} 个子域名")
            else:
                print(f"[-] {source_name:<15} 未发现子域名")
        except Exception as e:
            print(f"[-] {source_name:<15} 查询失败: {str(e)}")
    
    # 打印汇总信息
    print("\n" + "=" * 60)
    print(f"[*] 测试完成，总计发现 {len(total_domains)} 个唯一子域名")
    print("=" * 60)
    
    return total_domains

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("使用方法: python test_public_dns.py <domain>")
        print("示例: python test_public_dns.py example.com")
        sys.exit(1)
    
    discovered_domains = test_public_dns_search(sys.argv[1]) 