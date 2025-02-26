#!/usr/bin/env python3

class Colors:
    """ANSI 颜色代码"""
    
    # 前景色 - 使用更柔和的色调
    BLACK = '\033[30m'
    RED = '\033[38;5;203m'      # 柔和的红色
    GREEN = '\033[38;5;114m'    # 淡绿色
    YELLOW = '\033[38;5;221m'   # 暖黄色
    BLUE = '\033[38;5;75m'      # 天蓝色
    MAGENTA = '\033[38;5;176m'  # 淡紫色
    CYAN = '\033[38;5;80m'      # 青绿色
    WHITE = '\033[38;5;252m'    # 柔和的白色
    GRAY = '\033[38;5;246m'     # 中灰色
    
    # 高亮色 - 用于重要信息
    BRIGHT_RED = '\033[38;5;196m'    # 鲜艳的红色
    BRIGHT_GREEN = '\033[38;5;120m'  # 鲜艳的绿色
    BRIGHT_BLUE = '\033[38;5;81m'    # 鲜艳的蓝色
    BRIGHT_CYAN = '\033[38;5;87m'    # 鲜艳的青色
    BRIGHT_WHITE = '\033[38;5;255m'  # 纯白色
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # 样式
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    
    # 重置
    RESET = '\033[0m'
    
    @staticmethod
    def success(text: str) -> str:
        """成功信息（柔和的绿色）"""
        return f"{Colors.GREEN}{text}{Colors.RESET}"
    
    @staticmethod
    def warning(text: str) -> str:
        """警告信息（暖黄色）"""
        return f"{Colors.YELLOW}{text}{Colors.RESET}"
    
    @staticmethod
    def error(text: str) -> str:
        """错误信息（柔和的红色）"""
        return f"{Colors.RED}{text}{Colors.RESET}"
    
    @staticmethod
    def info(text: str) -> str:
        """普通信息（天蓝色）"""
        return f"{Colors.BLUE}{text}{Colors.RESET}"
    
    @staticmethod
    def gray(text: str) -> str:
        """灰色文本"""
        return f"{Colors.GRAY}{text}{Colors.RESET}"
    
    @staticmethod
    def title(text: str) -> str:
        """标题文本（鲜艳的蓝色加粗）"""
        return f"{Colors.BRIGHT_BLUE}{Colors.BOLD}{text}{Colors.RESET}"
    
    @staticmethod
    def highlight(text: str) -> str:
        """高亮文本（鲜艳的青色加粗）"""
        return f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{text}{Colors.RESET}"
    
    @staticmethod
    def dim(text: str) -> str:
        """暗色文本（中灰色）"""
        return f"{Colors.GRAY}{text}{Colors.RESET}"
    
    @staticmethod
    def section(text: str) -> str:
        """分节标题（鲜艳的绿色加粗下划线）"""
        return f"{Colors.BRIGHT_GREEN}{Colors.BOLD}{Colors.UNDERLINE}{text}{Colors.RESET}"
    
    @staticmethod
    def banner(text: str) -> str:
        """横幅文本（渐变色）"""
        # 使用多种颜色创建渐变效果
        colors = [
            '\033[38;5;51m',  # 浅蓝色
            '\033[38;5;45m',  # 青色
            '\033[38;5;39m',  # 深青色
            '\033[38;5;33m',  # 蓝色
            '\033[38;5;27m'   # 深蓝色
        ]
        lines = text.split('\n')
        colored_lines = []
        for i, line in enumerate(lines):
            color = colors[i % len(colors)]
            colored_lines.append(f"{color}{line}")
        return '\n'.join(colored_lines) + Colors.RESET 