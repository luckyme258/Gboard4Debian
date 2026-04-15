#!/usr/bin/env python3
"""
将 Rime 的 custom_phrase.txt 转换为 Gboard 导入格式
自动识别语言标签：包含中文 -> zh-CN，否则 -> zz
用法:
    python3 rime2gboard.py [输入文件] [输出文件]
示例:
    python3 rime2gboard.py custom_phrase.txt dictionary666.txt
"""

import sys
import re
from pathlib import Path

def contains_chinese(text):
    """判断字符串是否包含中文字符（Unicode 4E00-9FFF）"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def parse_rime_phrase(file_path):
    """解析 Rime custom_phrase.txt，返回 [(shortcut, word), ...]"""
    entries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                word = parts[0].strip()
                shortcut = parts[1].strip()
                if word and shortcut:
                    entries.append((shortcut, word))
    return entries

def write_gboard_file(entries, output_path):
    """写入 Gboard 格式：shortcut\tword\tlanguage_tag\tpos_tag"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Gboard Dictionary version:2\n")
        f.write("# Gboard Dictionary format:shortcut\tword\tlanguage_tag\tpos_tag\n")
        for shortcut, word in entries:
            if contains_chinese(word):
                lang = "zh-CN"
            else:
                lang = "zz"   # 用户要求：非中文使用 zz
            f.write(f"{shortcut}\t{word}\t{lang}\t\n")

def main():
    input_file = "custom_phrase.txt"
    output_file = "dictionary666.txt"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"错误：输入文件 {input_file} 不存在")
        sys.exit(1)
    
    entries = parse_rime_phrase(input_path)
    if not entries:
        print("警告：未找到任何有效短语")
    
    write_gboard_file(entries, output_file)
    print(f"转换完成！共 {len(entries)} 条短语")
    print(f"输出文件：{output_file}")
    print("可以直接将此文件导入 Gboard 个人词典。")

if __name__ == "__main__":
    main()