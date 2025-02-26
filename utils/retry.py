#!/usr/bin/env python3

import time
import functools
from datetime import datetime
from utils.colors import Colors

def retry_on_error(max_retries=3, delay=1):
    """网络请求重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:  # 最后一次尝试
                        raise  # 重新抛出异常
                    
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{Colors.info(timestamp)}][{Colors.warning('!')}] "
                          f"{Colors.warning(f'请求失败 ({str(e)})，{delay} 秒后进行第 {attempt + 2} 次重试...')}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator 