#!/usr/bin/env python3

import os
import sys

def remove_wx_prefixes(input_file='dict/test.txt', output_file=None):
    """清理词典文件，去除以 wx 开头的行以及包含特殊字符的行，并去重"""
    
    # 获取脚本所在目录的上级目录（项目根目录）
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(root_dir, input_file)
    
    # 如果没有指定输出文件，则使用原文件名加上 .clean 后缀
    if output_file is None:
        output_file = f"{input_file}.clean"
    output_path = os.path.join(root_dir, output_file)
    
    # 确保输入文件存在
    if not os.path.exists(input_path):
        print(f"错误: 输入文件 {input_path} 不存在")
        return False
    
    try:
        # 读取文件并过滤行
        total_lines = 0
        filtered_lines = 0
        duplicate_lines = 0
        clean_lines_set = set()  # 使用集合去重
        
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                total_lines += 1
                line = line.strip()
                
                # 过滤条件：以wx开头或包含*或@
                if line.startswith('wx') or '*' in line or '@' in line:
                    filtered_lines += 1
                    continue
                
                if line:  # 只保留非空行
                    # 检查是否已存在（去重）
                    if line in clean_lines_set:
                        duplicate_lines += 1
                        continue
                    
                    clean_lines_set.add(line)
        
        # 将集合转换为排序列表
        clean_lines = sorted(clean_lines_set)
        
        # 写入清理后的文件
        with open(output_path, 'w', encoding='utf-8') as f:
            for line in clean_lines:
                f.write(f"{line}\n")
        
        print(f"处理完成:")
        print(f"- 总行数: {total_lines}")
        print(f"- 过滤掉的行数: {filtered_lines}")
        print(f"- 重复行数: {duplicate_lines}")
        print(f"- 保留行数: {len(clean_lines)}")
        print(f"- 清理后的文件已保存到: {output_path}")
        return True
    
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 可以接受输入文件和输出文件作为参数
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'dict/test.txt'
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    remove_wx_prefixes(input_file, output_file) 