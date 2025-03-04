#!/usr/bin/env python3

from typing import Dict, List, Set, Tuple
from utils.logger import log_info, log_error, log_warning, log_success
from utils.colors import Colors
import dns.resolver
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

class SubdomainTakeoverChecker:
    """子域名接管风险检测类"""
    
    # 可能存在接管风险的 CNAME 指纹
    FINGERPRINTS = {
        'github.io': {
            'service': 'GitHub Pages',
            'nxdomain': True,  # 是否需要确认目标域名 NXDOMAIN
            'verify_endpoint': '{}.github.io',  # 验证端点
            'status_code': 404  # 期望的状态码
        },
        'amazonaws.com': {
            'service': 'AWS/S3',
            'nxdomain': True,
            'verify_endpoint': 'http://{}.s3.amazonaws.com',
            'status_code': 404
        },
        'azure.net': {
            'service': 'Azure',
            'nxdomain': True,
            'verify_endpoint': 'https://{}.azurewebsites.net',
            'status_code': 404
        },
        'cloudfront.net': {
            'service': 'CloudFront',
            'nxdomain': True,
            'verify_endpoint': 'http://{}',
            'status_code': 404
        },
        'herokuapp.com': {
            'service': 'Heroku',
            'nxdomain': True,
            'verify_endpoint': 'https://{}.herokuapp.com',
            'status_code': 404
        },
        # 添加阿里云 OSS 指纹
        'oss-cn-': {  # 匹配所有地域的 OSS
            'service': 'Aliyun OSS',
            'nxdomain': True,
            'verify_endpoint': 'http://{}',
            'status_code': 404,
            'body_pattern': 'The specified bucket does not exist'  # OSS 特有的错误信息
        },
        'oss.aliyuncs.com': {  # 通用域名
            'service': 'Aliyun OSS',
            'nxdomain': True,
            'verify_endpoint': 'http://{}',
            'status_code': 404,
            'body_pattern': 'The specified bucket does not exist'
        },
        # 添加腾讯云 COS 指纹
        'cos.ap-': {  # 匹配所有地域的 COS
            'service': 'Tencent COS',
            'nxdomain': True,
            'verify_endpoint': 'http://{}',
            'status_code': 404,
            'body_pattern': 'NoSuchBucket'  # COS 特有的错误信息
        },
        'cos.accelerate.myqcloud.com': {  # 全球加速域名
            'service': 'Tencent COS',
            'nxdomain': True,
            'verify_endpoint': 'http://{}',
            'status_code': 404,
            'body_pattern': 'NoSuchBucket'
        },
        'file.myqcloud.com': {  # 自定义域名
            'service': 'Tencent COS',
            'nxdomain': True,
            'verify_endpoint': 'http://{}',
            'status_code': 404,
            'body_pattern': 'NoSuchBucket'
        }
        # 可以继续添加其他服务的指纹
    }
    
    def __init__(self, domain: str, dns_records: Dict[str, Dict[str, List[str]]], debug: bool = False):
        """
        初始化检测器
        
        Args:
            domain: 目标域名
            dns_records: DNS 解析记录 {'subdomain': {'A': [], 'CNAME': []}}
            debug: 是否显示调试信息
        """
        self.domain = domain
        self.dns_records = dns_records
        self.debug = debug
        self.vulnerable_domains: Dict[str, Dict] = {}
        
    def check_domain(self, subdomain: str, cname: str) -> Tuple[bool, str, str]:
        """
        检查单个子域名是否存在接管风险
        
        Returns:
            (is_vulnerable, service_name, details)
        """
        # 检查 CNAME 是否匹配任何已知指纹
        for fingerprint, config in self.FINGERPRINTS.items():
            if fingerprint in cname.lower():
                service = config['service']
                
                # 检查 NXDOMAIN
                if config['nxdomain']:
                    try:
                        dns.resolver.resolve(cname, 'A')
                        # 如果能解析，说明目标正常
                        return False, service, "CNAME 目标可以正常解析"
                    except dns.resolver.NXDOMAIN:
                        # NXDOMAIN，继续检查
                        pass
                    except Exception as e:
                        if self.debug:
                            log_error(f"检查 {cname} 时出错: {str(e)}")
                        return False, service, f"检查出错: {str(e)}"
                
                # 尝试访问验证端点
                try:
                    endpoint = config['verify_endpoint'].format(cname)
                    response = requests.get(endpoint, timeout=10, verify=False)
                    
                    # 检查状态码
                    if response.status_code == config['status_code']:
                        # 如果配置了响应体模式，还需要检查响应内容
                        if 'body_pattern' in config:
                            if config['body_pattern'] in response.text:
                                return True, service, f"发现未注册的 {service} 服务"
                        else:
                            return True, service, f"发现未注册的 {service} 服务"
                except Exception as e:
                    if self.debug:
                        log_error(f"访问 {endpoint} 时出错: {str(e)}")
                
        return False, "", "不匹配任何已知指纹"
    
    def check_all(self) -> Dict[str, Dict]:
        """检查所有子域名"""
        domains_to_check = []
        
        # 收集所有需要检查的域名
        for subdomain, records in self.dns_records.items():
            if 'CNAME' in records and records['CNAME']:
                for cname in records['CNAME']:
                    domains_to_check.append((subdomain, cname))
        
        if not domains_to_check:
            log_info("未发现需要检查的 CNAME 记录")
            return {}
            
        
        # 使用线程池并发检查
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_domain = {
                executor.submit(self.check_domain, subdomain, cname): (subdomain, cname)
                for subdomain, cname in domains_to_check
            }
            
            for future in as_completed(future_to_domain):
                subdomain, cname = future_to_domain[future]
                try:
                    is_vulnerable, service, details = future.result()
                    if is_vulnerable:
                        log_warning(f"发现可能存在接管风险的子域名: {subdomain}")
                        log_warning(f"  - CNAME: {cname}")
                        log_warning(f"  - 服务: {service}")
                        log_warning(f"  - 详情: {details}")
                        
                        self.vulnerable_domains[subdomain] = {
                            'cname': cname,
                            'service': service,
                            'details': details
                        }
                except Exception as e:
                    if self.debug:
                        log_error(f"检查 {subdomain} 时出错: {str(e)}")
        
        # 打印结果统计
        if self.vulnerable_domains:
            print(Colors.BLUE + "\n" + "=" * 70)
            print(f"{Colors.section('检测结果')}")
            print(f"{Colors.warning('发现')} {Colors.highlight(len(self.vulnerable_domains))} {Colors.warning('个可能存在接管风险的子域名')}")
            print("=" * 70 + Colors.RESET)
        else:
            log_success("未发现存在接管风险的子域名")
            
        return self.vulnerable_domains

def check_takeover(domain: str, dns_records: Dict[str, Dict[str, List[str]]], debug: bool = False) -> Dict[str, Dict]:
    """
    检查子域名接管风险
    
    Args:
        domain: 目标域名
        dns_records: DNS 解析记录
        debug: 是否显示调试信息
    
    Returns:
        Dict[str, Dict]: 检测结果
    """
    checker = SubdomainTakeoverChecker(domain, dns_records, debug)
    return checker.check_all() 