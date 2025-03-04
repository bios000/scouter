import dns.resolver
import dns.exception
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from tqdm import tqdm
import json
import csv
from utils.logger import log_error, log_info ,log_warning,log_success
from utils.colors import Colors

import random
import time
import string
from concurrent.futures import as_completed
import os
import subprocess
from modules.check.takeover import check_takeover

class SubdomainFinder:
    def __init__(self, domain, debug=False):
        self.domain = domain
        self.subdomains = set()
        self.dns_records = {}
        self.debug = debug
        
        # 设置 DNS 服务器及其初始权重
        self.server_weights = {
            '8.8.8.8': 10,    # Google DNS
            '8.8.4.4': 8,
            # '1.1.1.1': 8,    # Cloudflare
            # '1.0.0.1': 6,
            '208.67.222.222': 8,  # OpenDNS
            '208.67.220.220': 6,
            '114.114.114.114': 10, #114DNS
            '114.114.115.115': 6,
            '119.29.29.29': 10, #tenent
            '182.254.116.116': 8, 
            
        }
        
        # 检查 nameservers 可用性
        self.nameservers = self._check_nameservers_availability()
        
        if not self.nameservers:
            raise Exception("没有可用的 DNS 服务器")
        
        # DNS 服务器性能统计
        self.server_stats = {
            server: {
                'success': 0,
                'failure': 0,
                'latency': [],
                'weight': self.server_weights[server]
            }
            for server in self.nameservers
        }
        
        # 设置超时和重试
        self.timeout = 1
        self.tries = 1
        
        # 修改泛解析相关的属性
        self.has_wildcard = False
        self.wildcard_records = []  # 存储 (ip_set, ttl) 元组
        
        # 直接调用同步方法检查泛解析
        self._check_wildcard_dns(debug)
    
    def _check_wildcard_dns(self, debug=False):
        """检查泛解析，同时考虑 IP 和 TTL"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.info('正在检查泛解析...')}")
        
        try:
            # 生成5个随机子域名
            random_domains = [f"{self._generate_random_domain()}.{self.domain}" for _ in range(5)]
            if debug:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.info('测试域名:')} {Colors.highlight(', '.join(random_domains))}")
            
            # 随机选择两个 nameserver
            selected_nameservers = random.sample(self.nameservers, min(2, len(self.nameservers)))
            
            # 在开始检测前就输出使用的DNS服务器
            if debug:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.info('使用的DNS服务器:')} {Colors.highlight(', '.join(selected_nameservers))}")
            
            # 创建同步 DNS 解析器
            resolver = dns.resolver.Resolver()
            resolver.nameservers = selected_nameservers
            resolver.timeout = 2
            resolver.lifetime = 2
            
            wildcard_records = []  # 存储 (ip_set, ttl) 元组
            
            # 解析这些随机域名
            for domain in random_domains:
                # 添加重试逻辑
                max_retries = 2
                retry_count = 0
                
                while retry_count <= max_retries:
                    try:
                        answers = resolver.resolve(domain, 'A')
                        ips = set(str(rdata.address) for rdata in answers)
                        ttl = answers.rrset.ttl  # 获取 TTL
                        
                        if ips:
                            if debug:
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.highlight(domain)} -> "
                                      f"{Colors.BRIGHT_WHITE}{', '.join(ips)} (TTL: {ttl})")
                            wildcard_records.append((ips, ttl))
                        break  # 成功解析，跳出重试循环
                    
                    except dns.resolver.NXDOMAIN:
                        if debug:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.highlight(domain)} -> {Colors.warning('域名不存在')}")
                        break  # 域名不存在，不需要重试
                    
                    except dns.resolver.NoAnswer:
                        if debug:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.highlight(domain)} -> {Colors.warning('无记录')}")
                        break  # 无记录，不需要重试
                    
                    except dns.resolver.Timeout:
                        retry_count += 1
                        if retry_count <= max_retries:
                            if debug:
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.highlight(domain)} -> "
                                      f"{Colors.warning(f'查询超时，正在重试 ({retry_count}/{max_retries})...')}")
                            # 切换到另一个 nameserver 进行重试
                            if len(self.nameservers) > 2:
                                new_nameserver = random.choice([ns for ns in self.nameservers if ns not in resolver.nameservers])
                                resolver.nameservers = [new_nameserver]
                                if debug:
                                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] 切换到 DNS 服务器: {Colors.highlight(new_nameserver)}")
                        else:
                            if debug:
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.highlight(domain)} -> {Colors.error('查询超时，已达最大重试次数')}")
                    
                    except Exception as e:
                        if debug:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.highlight(domain)} -> {Colors.error(f'查询失败: {str(e)}')}")
                        break  # 其他错误，不重试
            
            # 检查是否存在泛解析（IP集合和TTL都相同）
            if len(wildcard_records) >= 4:  # 需要4个都解析成功
                first_record = wildcard_records[0]
                if all(record == first_record for record in wildcard_records):
                    self.has_wildcard = True
                    self.wildcard_records = wildcard_records
                    log_warning(f"发现泛解析,IP: {', '.join(first_record[0])}, TTL: {first_record[1]}")
                    return
            
            log_info('未发现泛解析')
            
        except Exception as e:
            log_error(f'检查泛解析时出错: {str(e)}')
    
    def _generate_random_domain(self, length: int = None) -> str:
        """生成随机子域名"""
        if not length:
            length = random.randint(8, 12)
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def is_valid_subdomain(self, domain: str, records: Dict[str, List[str]]) -> bool:
        """检查解析结果是否为有效子域名（必须有 A 记录且不是泛解析）"""
        # 首先检查是否有 A 记录
        if not records or 'A' not in records or not records['A']:
            return False
        
        # 如果有泛解析，检查是否与泛解析记录匹配
        if self.has_wildcard:
            resolved_ips = set(records['A'])
            # 获取记录的 TTL
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = self.get_nameservers()
                answers = resolver.resolve(domain, 'A')
                current_ttl = answers.rrset.ttl
                
                # 检查 IP 集合和 TTL 是否与任何泛解析记录匹配
                for wildcard_ips, wildcard_ttl in self.wildcard_records:
                    if resolved_ips == wildcard_ips and current_ttl == wildcard_ttl:
                        return False
                
            except Exception:
                # 如果无法获取 TTL，仅比较 IP
                for wildcard_ips, _ in self.wildcard_records:
                    if resolved_ips == wildcard_ips:
                        return False
        
        return True
    
    def _check_nameservers_availability(self) -> List[str]:
        """检查 DNS 服务器可用性并保存可用服务器到文件"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.info('正在检查 DNS 服务器可用性...')}")
        
        available_servers = []
        test_domain = "www.baidu.com"
        resolver_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dict', 'resolver.txt')
        
        # 测试所有DNS服务器
        for server in self.server_weights.keys():
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [server]
                resolver.timeout = 2
                resolver.lifetime = 2
                
                start_time = time.time()
                try:
                    resolver.resolve(test_domain, 'A')
                    latency = time.time() - start_time
                    available_servers.append(server)
                    if self.debug:
                        log_info(f"DNS 服务器 {Colors.highlight(server)} 可用 (延迟: {latency:.3f}s)")
                except Exception:
                    if self.debug:
                        log_error(f"DNS 服务器 {Colors.highlight(server)} 不可用")
            except Exception as e:
                log_error(f"DNS 服务器 {Colors.highlight(server)} 测试失败: {str(e)}")
        
        # 保存可用的服务器到文件
        if available_servers:
            try:
                os.makedirs(os.path.dirname(resolver_file), exist_ok=True)
                with open(resolver_file, 'w') as f:
                    for server in available_servers:
                        f.write(f"{server}\n")
                log_success(f"已将 {len(available_servers)} 个可用的 DNS 服务器保存到: {resolver_file}")
            except Exception as e:
                log_error(f"保存DNS服务器列表失败: {str(e)}")
        
        return available_servers

  

    def dns_brute(self, subdomains: set, max_threads: Optional[int] = None, debug=False):
        """使用 massdns 进行 DNS 爆破"""
        self.debug = debug
        
        # 准备文件路径
        result_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'result')
        os.makedirs(result_dir, exist_ok=True)
        
        domain_base = self.domain.replace('.', '_')
        temp_input = os.path.join(result_dir, f'{domain_base}_temp_input.txt')
        result_file = os.path.join(result_dir, f'{self.domain}.txt')
        wildcard_file = os.path.join(result_dir, f'{self.domain}_wildcard.txt')  # 添加泛解析记录文件
        resolver_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dict', 'resolver.txt')
        
        # 将子域名写入临时文件
        try:
            with open(temp_input, 'w') as f:
                for subdomain in subdomains:
                    f.write(f"{subdomain}\n")
            log_info(f'已将 {len(subdomains)} 个子域名写入临时文件')
        except Exception as e:
            log_error(f'写入临时文件失败: {str(e)}')
            return set(), {}
        
        try:
            # 执行 massdns
            log_info('开始使用 massdns 进行扫描...')
            
            # 使用 subprocess.run 执行命令
            result = subprocess.run([
                'massdns',
                '-r', resolver_file,  # 使用绝对路径
                '-t', 'A',
                '-o', 'J',
                '-w', result_file,
                temp_input
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            
            if result.returncode != 0:
                log_error('massdns 执行失败')
                return set(), {}
            
            # 读取结果文件并处理
            valid_domains = set()
            valid_records = {}
            
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    for line in f:
                        try:
                            # 解析JSON格式的结果
                            result = json.loads(line.strip())
                            domain = result['name'].rstrip('.')  # 移除末尾的点
                            
                            if result['status'] == 'NOERROR' and 'data' in result:
                                answers = result['data'].get('answers', [])
                                
                                # 初始化该域名的记录
                                if domain not in valid_records:
                                    valid_records[domain] = {'A': [], 'CNAME': []}
                                
                                # 处理每个答案
                                has_a_record = False  # 标记是否有A记录
                                for answer in answers:
                                    if answer['type'] == 'A':
                                        valid_records[domain]['A'].append(answer['data'])
                                        has_a_record = True
                                    elif answer['type'] == 'CNAME':
                                        valid_records[domain]['CNAME'].append(answer['data'].rstrip('.'))
                                
                                # 只有当有A记录时才添加到有效域名集合
                                if has_a_record:
                                    valid_domains.add(domain)
                                    valid_records[domain] = {'A': valid_records[domain]['A'], 'CNAME': valid_records[domain]['CNAME']}
                                elif valid_records[domain]['CNAME']:
                                    # 如果只有 CNAME 记录,检查是否可能被接管
                                    temp_records = {domain: valid_records[domain]}
                                    takeover_results = check_takeover(self.domain, temp_records, self.debug)
                                    
                                    if takeover_results:
                                        # 如果发现接管风险,也将其添加到有效域名集合
                                        valid_domains.add(domain)
                                        valid_records[domain] = {'A': [], 'CNAME': valid_records[domain]['CNAME']}
                                        log_warning(f"域名 {Colors.highlight(domain)} 只有CNAME记录且存在接管风险!")
                                        for info in takeover_results.values():
                                            log_warning(f"  - CNAME: {Colors.highlight(info['cname'])}")
                                            log_warning(f"  - 服务: {Colors.highlight(info['service'])}")
                                            log_warning(f"  - 详情: {Colors.highlight(info['details'])}")
                                    elif self.debug:
                                        log_info(f"域名 {Colors.highlight(domain)} 只有CNAME记录: {Colors.highlight(', '.join(valid_records[domain]['CNAME']))}")
                        except json.JSONDecodeError as e:
                            if self.debug:
                                log_error(f'JSON解析失败: {str(e)}')
                            continue
                        except Exception as e:
                            if self.debug:
                                log_error(f'处理结果行失败: {str(e)}')
                            continue
                
                # 检查泛解析
                if self.has_wildcard:
                    wildcard_ips = set()
                    for ips, _ in self.wildcard_records:  # 忽略 TTL
                        wildcard_ips.update(ips)
                    
                    filtered_domains = set()
                    filtered_records = {}
                    wildcard_hit_count = 0
                    
                    # 预先读取所有结果到内存
                    domain_results = {}
                    try:
                        with open(result_file, 'r') as f:
                            for line in f:
                                result = json.loads(line.strip())
                                domain = result['name'].rstrip('.')
                                domain_results[domain] = result
                    except Exception as e:
                        if self.debug:
                            log_error(f'读取结果文件失败: {str(e)}')
                        return valid_domains, valid_records
                    
                    def check_domain_wildcard(domain):
                        """检查单个域名是否命中泛解析"""
                        try:
                            records = valid_records[domain]
                            domain_ips = set(records['A'])
                            
                            # 只检查 IP 是否匹配泛解析
                            is_wildcard = domain_ips and domain_ips.issubset(wildcard_ips)
                            
                            # if is_wildcard and self.debug:
                            #     log_warning(f"域名 {Colors.highlight(domain)} 命中IP泛解析: "
                            #               f"{Colors.highlight(', '.join(domain_ips))}")
                            
                            return domain, records, is_wildcard
                            
                        except Exception as e:
                            if self.debug:
                                log_error(f'处理域名 {domain} 时出错: {str(e)}')
                            return domain, valid_records.get(domain), False
                    
                    # 使用线程池并行处理
                    with ThreadPoolExecutor(max_workers=min(32, len(valid_domains))) as executor:
                        futures = [executor.submit(check_domain_wildcard, domain) for domain in valid_domains]
                        
                        for future in as_completed(futures):
                            try:
                                domain, records, is_wildcard = future.result()
                                if is_wildcard:
                                    wildcard_hit_count += 1
                                else:
                                    filtered_domains.add(domain)
                                    filtered_records[domain] = records
                            except Exception as e:
                                if self.debug:
                                    log_error(f'处理结果时出错: {str(e)}')
                    
                    if self.debug:
                        log_warning(f"共发现 {Colors.highlight(str(wildcard_hit_count))} 个域名命中泛解析 "
                                  f"(IP: {Colors.highlight(', '.join(wildcard_ips))})")
                    
                    valid_domains = filtered_domains
                    valid_records = filtered_records
                
                log_success(f'扫描完成，发现 {len(valid_domains)} 个有效子域名')
            
            # 清理临时文件
            try:
                os.remove(temp_input)
                if self.debug:
                    log_info('已清理临时文件')
            except Exception as e:
                if self.debug:
                    log_error(f'清理临时文件失败: {str(e)}')
            
            return valid_domains, valid_records
            
        except Exception as e:
            log_error(f'执行过程中出错: {str(e)}')
            return set(), {}

    

