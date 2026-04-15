#!/usr/bin/env python3
"""
将 Rime 的 custom_phrase.txt 转换为 Gboard 导入格式
用法:
    python3 rime2gboard.py [输入文件] [输出文件]
示例:
    python3 rime2gboard.py custom_phrase.txt dictionary666.txt
"""

import sys
from pathlib import Path

def parse_rime_phrase(file_path):
    """
    解析 Rime custom_phrase.txt
    返回列表 [(shortcut, word), ...] 保持文件顺序
    """
    entries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            # 跳过空行和注释行（以 # 开头）
            if not line or line.startswith('#'):
                continue
            # 按制表符分割
            parts = line.split('\t')
            if len(parts) >= 2:
                word = parts[0].strip()
                shortcut = parts[1].strip()
                # 权重列可选，忽略
                if word and shortcut:
                    entries.append((shortcut, word))
    return entries

def write_gboard_file(entries, output_path):
    """写入 Gboard 格式：shortcut\tword\tzh-CN\t"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入 Gboard 头部（可选，但 Gboard 导入时会忽略以 # 开头的行）
        f.write("# Gboard Dictionary version:2\n")
        f.write("# Gboard Dictionary format:shortcut\tword\tlanguage_tag\tpos_tag\n")
        for shortcut, word in entries:
            f.write(f"{shortcut}\t{word}\tzh-CN\t\n")

def main():
    # 默认输入输出文件名
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