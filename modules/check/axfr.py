#!/usr/bin/env python3

import dns.zone
import dns.query
import dns.resolver
from typing import List, Dict, Set
from utils.logger import log_info, log_error, log_warning, log_success

class AXFRChecker:
    """域传送漏洞检测类"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.nameservers = set()
        
    def get_nameservers(self) -> Set[str]:
        """获取域名的 NS 记录"""
        try:
            answers = dns.resolver.resolve(self.domain, 'NS')
            for rdata in answers:
                ns = str(rdata.target).rstrip('.')
                # 解析 NS 服务器的 IP
                try:
                    ip_answers = dns.resolver.resolve(ns, 'A')
                    for ip in ip_answers:
                        self.nameservers.add(str(ip))
                except:
                    continue
                    
            if self.nameservers:
                log_info(f"发现 {len(self.nameservers)} 个 NS 服务器")
            else:
                log_warning("未发现任何 NS 服务器")
                
        except Exception as e:
            log_error(f"获取 NS 记录失败: {str(e)}")
            
        return self.nameservers
    
    def check_axfr(self) -> Dict[str, List[str]]:
        """检测域传送漏洞
        
        Returns:
            Dict[str, List[str]]: 存在漏洞的 NS 服务器及其解析到的域名
        """
        results = {}
        
        if not self.nameservers:
            self.get_nameservers()
            
        if not self.nameservers:
            return results
            
        for ns in self.nameservers:
            try:
                # 尝试进行域传送
                zone = dns.zone.from_xfr(dns.query.xfr(ns, self.domain))
                
                # 如果成功获取到区域传送数据
                if zone:
                    log_success(f"发现域传送漏洞! NS 服务器: {ns}")
                    results[ns] = []
                    
                    # 提取所有记录
                    for name, node in zone.nodes.items():
                        name = str(name)
                        if name != '@':
                            full_domain = f"{name}.{self.domain}"
                            results[ns].append(full_domain)
                            
                    log_success(f"从 {ns} 获取到 {len(results[ns])} 条记录")
                    
            except Exception as e:
                continue
                
        return results
    
    def run(self) -> Dict[str, List[str]]:
        """运行检测
        
        Returns:
            Dict[str, List[str]]: 检测结果
        """
        log_info(f"开始检测域传送漏洞: {self.domain}")
        results = self.check_axfr()
        

            
        return results

def check_axfr(domain: str) -> Dict[str, List[str]]:
    """检测指定域名是否存在域传送漏洞
    
    Args:
        domain: 目标域名
    
    Returns:
        Dict[str, List[str]]: 检测结果
    """
    checker = AXFRChecker(domain)
    return checker.run()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <domain>")
        sys.exit(1)
    check_axfr(sys.argv[1])
