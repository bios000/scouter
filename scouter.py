#!/usr/bin/env python3

import argparse
import sys
from utils.dns_resolver import SubdomainFinder
import json
import csv
from datetime import datetime
import time
from modules.ct.scraper import get_ct_subdomains
from modules.public.scraper import get_public_dns_subdomains
from modules.code.scraper import get_code_subdomains
import os
from utils.config import Config, init_config
from modules.search.scraper import get_search_engine_subdomains
from utils.colors import Colors
from utils.logger import log_info, log_success, log_error, log_warning
import asyncio



def print_banner():
    """打印工具横幅"""
    banner = Colors.CYAN + """
    ███████╗ ██████╗ ██████╗ ██╗   ██╗████████╗███████╗██████╗ 
    ██╔════╝██╔════╝██╔═══██╗██║   ██║╚══██╔══╝██╔════╝██╔══██╗
    ███████╗██║     ██║   ██║██║   ██║   ██║   █████╗  ██████╔╝
    ╚════██║██║     ██║   ██║██║   ██║   ██║   ██╔══╝  ██╔══██╗
    ███████║╚██████╗╚██████╔╝╚██████╔╝   ██║   ███████╗██║  ██║
    ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                Version: 1.0.0
                                                Author: bios000
    """ + Colors.RESET
    print(banner)
    print(Colors.BLUE + "=" * 70)
    print(f"[*] 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n" + Colors.RESET)

def save_results(subdomains, output_file, output_format, dns_records=None):
    """
    保存结果到指定格式的文件
    
    Args:
        subdomains: 有效子域名集合
        output_file: 输出文件名
        output_format: 输出格式 (json, csv, txt)
        dns_records: DNS记录字典，默认为None
    """
    dns_records = dns_records or {}
    
    try:
        with open(output_file, 'w') as f:
            if output_format == 'json':
                results = []
                for subdomain in sorted(subdomains):  # 直接使用传入的子域名集合
                    records = dns_records.get(subdomain, {})
                    ips = []
                    if 'A' in records:
                        ips.extend(records['A'])
                    results.append({
                        "domain": subdomain,
                        "ip": ips
                    })
                json.dump(results, f, indent=4)
                log_success('结果已保存为 JSON 格式')
            elif output_format == 'csv':
                writer = csv.writer(f)
                writer.writerow(['subdomain', 'ip'])
                for subdomain in sorted(subdomains):  # 直接使用传入的子域名集合
                    records = dns_records.get(subdomain, {})
                    ips = []
                    if 'A' in records:
                        ips.extend(records['A'])
                    writer.writerow([subdomain, ','.join(ips)])
                log_success('结果已保存为 CSV 格式')
            elif output_format == 'txt':
                for subdomain in sorted(subdomains):  # 直接使用传入的子域名集合
                    records = dns_records.get(subdomain, {})
                    ips = []
                    if 'A' in records:
                        ips.extend(records['A'])
                    if ips:
                        f.write(f"{subdomain} {','.join(ips)}\n")
                    else:
                        f.write(f"{subdomain}\n")
                log_success('结果已保存为 TXT 格式')
                    
    except Exception as e:
        log_error(f"保存结果失败: {str(e)}")
        sys.exit(1)

def get_default_wordlist():
    """获取默认字典路径"""
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dict', 'test.txt')
    if not os.path.exists(default_path):
        raise FileNotFoundError(f"默认字典文件不存在: {default_path}")
    return default_path

def get_project_root() -> str:
    """获取项目根目录路径"""
    # 返回当前脚本所在目录作为项目根目录
    return os.path.dirname(os.path.abspath(__file__))

def get_result_dir() -> str:
    """获取结果目录路径，如果不存在则创建"""
    result_dir = os.path.join(get_project_root(), 'result')
    os.makedirs(result_dir, exist_ok=True)
    return result_dir

def get_output_path(domain: str, output_format: str) -> str:
    """
    获取输出文件路径
    
    Args:
        domain: 目标域名
        output_format: 输出格式 (json, csv, txt)
    Returns:
        输出文件的完整路径
    """
    return os.path.join(get_result_dir(), f"{domain}.{output_format}")

async def main():
    # 确保结果目录存在
    result_dir = get_result_dir()
    if not os.path.exists(result_dir):
        try:
            os.makedirs(result_dir)
            log_info(f"创建结果目录: {result_dir}")
        except Exception as e:
            log_error(f"创建结果目录失败: {str(e)}")
            return
    
    parser = argparse.ArgumentParser(description='Subdomain discovery tool.')
    
    # 添加配置管理子命令
    subparsers = parser.add_subparsers(dest='command', help='commands')
    
    # 配置管理命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_parser.add_argument('--init', action='store_true', help='初始化配置')
    config_parser.add_argument('--set', help='设置 API 密钥，格式: service:key 或 service:key_type:value')
    config_parser.add_argument('--get', help='获取 API 密钥，格式: service 或 service:key_type')
    config_parser.add_argument('--list', action='store_true', help='列出所有配置')
    
    # 子域名扫描命令
    scan_parser = subparsers.add_parser('scan', help='子域名扫描')
    scan_parser.add_argument('-d', '--domain', required=True, help='目标域名')
    scan_parser.add_argument('-w', '--wordlist', help='DNS爆破字典文件')
    
    # 修改输出文件参数
    output_group = scan_parser.add_argument_group('输出选项')
    output_group.add_argument('-t', '--txt', nargs='?', const='default', metavar='FILE', help='保存为 TXT 格式 (不指定文件名则使用默认)')
    output_group.add_argument('-j', '--json', nargs='?', const='default', metavar='FILE', help='保存为 JSON 格式 (不指定文件名则使用默认)')
    output_group.add_argument('-c', '--csv', nargs='?', const='default', metavar='FILE', help='保存为 CSV 格式 (不指定文件名则使用默认)')
    
    scan_parser.add_argument('--debug', action='store_true', help='显示调试信息')
    
    # 数据源选项
    source_group = scan_parser.add_argument_group('数据源选项')
    source_group.add_argument('--ct', action='store_true', help='使用证书透明度日志')
    source_group.add_argument('--brute', action='store_true', help='使用DNS爆破')
    source_group.add_argument('--code', action='store_true', help='使用代码仓库搜索')
    source_group.add_argument('--public', action='store_true', help='使用公开DNS数据')
    source_group.add_argument('--search', action='store_true', help='使用搜索引擎')
    source_group.add_argument('--all', action='store_true', help='使用所有数据源')
    
    # 搜索引擎选项
    search_group = scan_parser.add_argument_group('搜索引擎选项')
    search_group.add_argument('--google', action='store_true', help='使用 Google 搜索')
    search_group.add_argument('--bing', action='store_true', help='使用 Bing 搜索')
    search_group.add_argument('--baidu', action='store_true', help='使用百度搜索')
    search_group.add_argument('--quake360', action='store_true', help='使用 360Quake 搜索')
    search_group.add_argument('--fofa', action='store_true', help='使用 FOFA 搜索')
    search_group.add_argument('--hunter', action='store_true', help='使用奇安信鹰图搜索')
    search_group.add_argument('--shodan', action='store_true', help='使用 Shodan 搜索')
    
    # 代码仓库选项
    code_group = scan_parser.add_argument_group('代码仓库选项')
    code_group.add_argument('--github', action='store_true', help='使用 GitHub 搜索')
    code_group.add_argument('--gitee', action='store_true', help='使用 Gitee 搜索')
    
    # CT 日志选项
    ct_group = scan_parser.add_argument_group('证书透明度日志选项')
    ct_group.add_argument('--crtsh', action='store_true', help='使用 crt.sh')
    ct_group.add_argument('--certspotter', action='store_true', help='使用 Certspotter')
    ct_group.add_argument('--censys', action='store_true', help='使用 Censys')
    ct_group.add_argument('--sslmate', action='store_true', help='使用 SSLMate')
    ct_group.add_argument('--racent', action='store_true', help='使用 Racent')
    
    # 公共 DNS 选项
    public_group = scan_parser.add_argument_group('公共 DNS 选项')
    public_group.add_argument('--ip138', action='store_true', help='使用 ip138')
    public_group.add_argument('--hackertarget', action='store_true', help='使用 Hackertarget')
    public_group.add_argument('--securitytrails', action='store_true', help='使用 SecurityTrails')
    public_group.add_argument('--netcraft', action='store_true', help='使用 Netcraft')
    public_group.add_argument('--robtex', action='store_true', help='使用 Robtex')
    public_group.add_argument('--dnsdumpster', action='store_true', help='使用 DNSDumpster')
    public_group.add_argument('--bevigil', action='store_true', help='使用 BeVigil')
    
    args = parser.parse_args()
    
    try:
        # 打印工具横幅
        print_banner()
        
        if args.command == 'config':
            config = Config()
            
            if args.init:
                # 初始化配置
                init_config()
                return
                
            elif args.set:
                # 设置 API 密钥
                parts = args.set.split(':')
                if len(parts) == 2:
                    service, key = parts
                    config.set_api_key(service, key)
                    print(f"[+] 已设置 {service} 的 API 密钥")
                elif len(parts) == 3:
                    service, key_type, value = parts
                    config.set_api_key(service, value, key_type)
                    print(f"[+] 已设置 {service} 的 {key_type} 为 {value}")
                else:
                    print("[-] 无效的格式，请使用 service:key 或 service:key_type:value")
                return
                
            elif args.get:
                # 获取 API 密钥
                parts = args.get.split(':')
                if len(parts) == 1:
                    service = parts[0]
                    key = config.get_api_key(service)
                    if key:
                        print(f"{service}: {key}")
                    else:
                        print(f"[-] 未找到 {service} 的 API 密钥")
                elif len(parts) == 2:
                    service, key_type = parts
                    key = config.get_api_key(service, key_type)
                    if key:
                        print(f"{service} {key_type}: {key}")
                    else:
                        print(f"[-] 未找到 {service} 的 {key_type}")
                return
                
            elif args.list:
                # 列出所有配置
                print("\n当前配置:")
                print("=" * 50)
                for service, value in config.config.items():
                    if isinstance(value, dict):
                        print(f"\n{service}:")
                        for k, v in value.items():
                            print(f"  {k}: {'*' * 8 if v else '未设置'}")
                    else:
                        print(f"\n{service}: {'*' * 8 if value else '未设置'}")
                print("=" * 50)
                return
            
            else:
                parser.print_help()
                return
                
        elif args.command == 'scan':
            start_time = time.time()
            all_subdomains = set()
            dns_records = {}
            
            
            # 证书透明度日志搜索
            if args.ct or args.crtsh or args.certspotter or args.censys or args.sslmate or args.racent or args.all:
                ct_domains = get_ct_subdomains(
                    args.domain,
                    crtsh=args.crtsh or args.all or args.ct,
                    certspotter=args.certspotter or args.all or args.ct,
                    censys=args.censys or args.all or args.ct,
                    sslmate=args.sslmate or args.all or args.ct,
                    racent=args.racent or args.all or args.ct
                )
                
                if ct_domains:
                    all_subdomains.update(ct_domains)
            
            # 公共 DNS 数据源
            if args.public or args.ip138 or args.hackertarget or args.securitytrails or args.netcraft or args.robtex or args.dnsdumpster or args.bevigil or args.all:
                public_domains = get_public_dns_subdomains(
                    args.domain,
                    ip138=args.ip138 or args.all or args.public,
                    hackertarget=args.hackertarget or args.all or args.public,
                    securitytrails=args.securitytrails or args.all or args.public,
                    netcraft=args.netcraft or args.all or args.public,
                    robtex=args.robtex or args.all or args.public,
                    dnsdumpster=args.dnsdumpster or args.all or args.public,
                    bevigil=args.bevigil or args.all or args.public
                )
                
                if public_domains:
                    all_subdomains.update(public_domains)
            
            # 代码仓库搜索
            if args.code or args.github or args.gitee or args.all:
                code_domains = get_code_subdomains(
                    args.domain,
                    github=args.github or args.all or args.code,
                    gitee=args.gitee or args.all or args.code
                )
                
                if code_domains:
                    all_subdomains.update(code_domains)
            
            # 搜索引擎子域名收集
            if args.search or args.google or args.bing or args.baidu or args.quake360 or args.fofa or args.hunter or args.shodan or args.all:
                search_domains = get_search_engine_subdomains(
                    args.domain,
                    google=args.google or args.all or args.search,
                    bing=args.bing or args.all or args.search,
                    baidu=args.baidu or args.all or args.search,
                    quake360=args.quake360 or args.all or args.search,
                    fofa=args.fofa or args.all or args.search,
                    hunter=args.hunter or args.all or args.search,
                    shodan=args.shodan or args.all or args.search
                )
                
                if search_domains:
                    all_subdomains.update(search_domains)
            
            
            
            # DNS爆破模式
            if args.brute or args.all:
                # 检查是否指定了字典文件
                default_wordlist = os.path.join(os.path.dirname(__file__), 'dict', 'test.txt')
                
                if not args.wordlist:
                    # 使用默认字典文件
                    if os.path.exists(default_wordlist):
                        args.wordlist = default_wordlist
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.info('*')}] {Colors.info(f'使用默认字典文件: {default_wordlist}')}")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.error('-')}] {Colors.error('未指定字典文件且默认字典文件不存在')}")
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{Colors.error('-')}] {Colors.error('请使用 -w/--wordlist 参数指定字典文件')}")
                        return

                # 读取字典文件并拼接子域名
                try:
                    with open(args.wordlist, 'r') as f:
                        subdomain_prefixes = f.read().splitlines()
                    
                    # 拼接完整子域名
                    brute_domains = {f"{prefix}.{args.domain}" for prefix in subdomain_prefixes}
                    
                    # 如果是 all 模式，将字典生成的子域名也加入总集合
                    all_subdomains.update(brute_domains)
                except Exception as e:
                    log_error(f"读取字典文件失败: {str(e)}")
                    return

            resolved_domains = set()
            # 开始进行 DNS 解析
            if len(all_subdomains) > 0:
                # 创建 DNS 解析器
                finder = SubdomainFinder(args.domain, debug=args.debug)
                
                all_subdomains = {s.lower() for s in all_subdomains}
                # 进行 DNS 解析
                resolved_domains, dns_records = finder.dns_brute(all_subdomains, debug=args.debug)
                
                if resolved_domains:
                    log_success(f"DNS 解析完成，发现 {len(resolved_domains)} 个有效子域名")
                    
                    # 确定输出文件和格式
                    output_file = None
                    output_format = 'txt'  # 默认格式
                    
                    if args.txt is not None:
                        output_format = 'txt'
                        output_file = args.txt if args.txt != 'default' else None
                    elif args.json is not None:
                        output_format = 'json'
                        output_file = args.json if args.json != 'default' else None
                    elif args.csv is not None:
                        output_format = 'csv'
                        output_file = args.csv if args.csv != 'default' else None
                    
                    # 如果没有指定输出文件，使用默认文件名
                    if not output_file or output_file == 'default':
                        output_file = os.path.join(get_result_dir(), f"{args.domain}.{output_format}")
                    else:
                        # 如果指定了完整路径，使用指定的路径
                        if not os.path.isabs(output_file):
                            output_file = os.path.join(get_result_dir(), output_file)
                    
                    # 确保输出目录存在
                    output_dir = os.path.dirname(output_file)
                    if not os.path.exists(output_dir):
                        try:
                            os.makedirs(output_dir)
                            log_info(f"创建输出目录: {output_dir}")
                        except Exception as e:
                            log_error(f"创建输出目录失败: {str(e)}")
                            return
                    
                    try:
                        save_results(resolved_domains, output_file, output_format, dns_records)
                        log_success(f"所有结果已保存到: {output_file}")
                    except Exception as e:
                        log_error(f"保存结果失败: {str(e)}")
                else:
                    log_error("未发现任何有效子域名")
            
            # 打印统计信息
            elapsed_time = time.time() - start_time
            print("\n" + Colors.BLUE + "=" * 70)
            print(f"[{Colors.info('*')}] {Colors.section('扫描统计')}:")
            print(f"{Colors.success('    - 目标域名:')} {Colors.highlight(args.domain)}")
            print(f"{Colors.success('    - 扫描用时:')} {Colors.BRIGHT_WHITE}{elapsed_time:.2f}{Colors.success(' 秒')}")
            print(f"{Colors.success('    - 有效子域名:')} {Colors.BRIGHT_WHITE}{len(resolved_domains)}{Colors.success(' 个')}")
            print(Colors.BLUE + "=" * 70 + Colors.RESET)
            
        else:
            parser.print_help()
            
    except Exception as e:
        log_error(f"执行过程中出错: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
