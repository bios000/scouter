from datetime import datetime
from utils.colors import Colors
import sys

def log_info(message):
    """打印信息日志"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{Colors.info(timestamp)}] [{Colors.info('*')}] {Colors.info(message)}")

def log_success(message):
    """打印成功日志"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{Colors.info(timestamp)}] [{Colors.success('+')}] {Colors.success(message)}")

def log_error(message):
    """打印错误日志"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{Colors.info(timestamp)}] [{Colors.error('-')}] {Colors.error(message)}", file=sys.stderr)

def log_warning(message):
    """打印警告日志"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{Colors.info(timestamp)}] [{Colors.warning('!')}] {Colors.warning(message)}") 