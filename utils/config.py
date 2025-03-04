#!/usr/bin/env python3

import os
from pathlib import Path
import json
from typing import Dict, Any, Optional

class Config:
    """配置管理类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'github': {
            'api_key': ''  # GitHub API Token
        },
        'gitee': {
            'access_token': ''  # Gitee Access Token
        },
        'censys': {
            'api_id': '',      # Censys API ID
            'api_secret': ''   # Censys API Secret
        },
        'securitytrails': {
            'api_key': ''      # SecurityTrails API Key
        },
        'fofa': {
            'api_key': ''      # FOFA API Key
        },
        'quake360': {
            'api_key': ''      # Quake360 API Token
        },
        'hunter': {  # 添加 Hunter 配置
            'api_key': ''
        },
        'shodan': {  # 添加 Shodan 配置
            'api_key': ''
        },
        'bevigil': {  # 添加 Bevigil 配置
            'api_key': ''
        },
        'fullhunt': {  # 添加 FullHunt 配置
            'api_key': ''      # FullHunt API Key
        },
        'urlscan': {
            'api_key': ''      # URLScan.io API Key
        },
        'alienvault': {
            'api_key': ''      # AlienVault API Key
        },
        'riskiq': {
            'api_key': '',     # RiskIQ API Key
            'api_secret': ''   # RiskIQ API Secret
        },
        'threatbook': {
            'api_key': ''      # 微步在线 API Key
        },
        'virustotal': {
            'api_key': ''      # VirusTotal API Key
        }
    }
    
    def __init__(self, config_file: str = None):
        """初始化配置
        
        Args:
            config_file: 配置文件路径，默认为 ~/.scouter/config.json
        """
        if config_file is None:
            home = os.path.expanduser("~")
            self.config_dir = os.path.join(home, '.scouter')
            self.config_file = os.path.join(self.config_dir, 'config.json')
        else:
            self.config_file = config_file
            self.config_dir = os.path.dirname(config_file)
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # 合并默认配置
            merged = self.DEFAULT_CONFIG.copy()
            for service, values in config.items():
                if service in merged:
                    if isinstance(merged[service], dict):
                        merged[service].update(values)
                    else:
                        merged[service] = values
                else:
                    merged[service] = values
            
            return merged
            
        except Exception as e:
            print(f"[-] 加载配置文件失败: {str(e)}")
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
                
        except Exception as e:
            print(f"[-] 保存配置文件失败: {str(e)}")
    
    def get_api_key(self, service: str, key_type: str = 'api_key') -> Optional[str]:
        """获取 API 密钥
        
        Args:
            service: 服务名称
            key_type: 密钥类型，默认为 api_key
        Returns:
            str: API 密钥，如果未配置则返回 None
        """
        if service not in self.config:
            return None
        
        if isinstance(self.config[service], dict):
            return self.config[service].get(key_type)
        
        return self.config[service] if key_type == 'api_key' else None
    
    def set_api_key(self, service: str, value: str, key_type: str = 'api_key'):
        """设置 API 密钥
        
        Args:
            service: 服务名称
            value: API 密钥值
            key_type: 密钥类型，默认为 api_key
        """
        if service not in self.config:
            self.config[service] = {}
        
        if isinstance(self.config[service], dict):
            self.config[service][key_type] = value
        else:
            self.config[service] = value if key_type == 'api_key' else {key_type: value}
        
        self.save_config()

def init_config():
    """初始化配置文件"""
    config = Config()
    config.save_config()
    print("[+] 配置文件已初始化")
    print(f"[*] 配置文件路径: {config.config_file}")

if __name__ == '__main__':
    init_config() 