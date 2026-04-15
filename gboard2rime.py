#!/usr/bin/env python3
"""
将 Gboard 导出的 dictionary.txt 转换为 Rime 的 custom_phrase.txt
支持增量合并（默认），避免丢失已有词库。
用法:
    python3 gboard2rime.py [输入文件] [输出文件]          # 合并模式（若输出存在）
    python3 gboard2rime.py --overwrite [输入文件] [输出文件] # 覆盖模式
示例:
    python3 gboard2rime.py dictionary.txt custom_phrase.txt
    python3 gboard2rime.py --merge new_dict.txt custom_phrase.txt
"""

import sys
import re
import argparse
from collections import defaultdict

def clean_word(word):
    """清理 word 字段，去除语言标签和多余空白"""
    if not word:
        return word
    # 去除末尾语言标签
    word = re.sub(r'\s*(zh-CN|zh-TW|zh-HK|en-US|ja-JP)\s*$', '', word, flags=re.IGNORECASE)
    # 取第一个空格前的内容
    parts = word.split()
    if parts:
        word = parts[0]
    return word.strip()

def parse_gboard(file_path):
    """读取 Gboard 文件，返回按顺序的 (shortcut, word) 列表，自动去重（按行顺序）"""
    entries = []
    seen = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                # 尝试按空白分割容错
                parts = line.split()
                if len(parts) < 2:
                    print(f"警告：第 {line_num} 行格式无效，已跳过：{line}")
                    continue
            shortcut = parts[0].strip()
            word = parts[1].strip()
            word = clean_word(word)
            if not shortcut or not word:
                print(f"警告：第 {line_num} 行缺少 shortcut 或 word，已跳过：{line}")
                continue
            key = (shortcut, word)
            if key not in seen:
                seen.add(key)
                entries.append((shortcut, word))
    return entries

def parse_existing_rime(file_path):
    """
    解析已有的 custom_phrase.txt，返回：
        entries: [(word, shortcut, weight), ...] 保持原有顺序
        max_weight_per_shortcut: dict {shortcut: max_weight}
    """
    entries = []
    max_weight = defaultdict(int)
    if not file_path.exists():
        return entries, max_weight
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                word = parts[0].strip()
                shortcut = parts[1].strip()
                try:
                    weight = int(parts[2].strip())
                except ValueError:
                    weight = 1
                entries.append((word, shortcut, weight))
                if weight > max_weight[shortcut]:
                    max_weight[shortcut] = weight
    return entries, max_weight

def merge_entries(new_gboard_entries, existing_rime_entries, existing_max_weight):
    """
    合并新条目到已有条目中：
        - 已有条目完全保留（顺序、权重不变）
        - 新条目中若 (shortcut, word) 已存在则跳过
        - 新条目的权重 = 当前 shortcut 的最大权重 + 1（依次递增）
    返回合并后的条目列表（保持原有顺序，新追加在末尾）
    """
    existing_set = {(word, shortcut) for (word, shortcut, _) in existing_rime_entries}
    new_entries_to_add = []
    # 复制当前最大权重字典，用于递增
    current_max = existing_max_weight.copy()
    for shortcut, word in new_gboard_entries:
        if (word, shortcut) in existing_set:
            print(f"跳过已存在条目: {word}\t{shortcut}")
            continue
        # 计算新权重
        current_max[shortcut] += 1
        new_weight = current_max[shortcut]
        new_entries_to_add.append((word, shortcut, new_weight))
        # 添加到已存在集合，避免同一批次内重复
        existing_set.add((word, shortcut))
    # 合并：先全部已有，再追加新
    merged = existing_rime_entries + new_entries_to_add
    return merged

def write_rime_file(entries, output_path):
    """写入 Rime 格式文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Rime table\n")
        f.write("# coding: utf-8\n")
        f.write("#@/db_name custom_phrase.txt\n")
        f.write("#@/db_type tabledb\n")
        f.write("#\n")
        f.write("# 用於『朙月拼音』系列輸入方案\n")
        f.write("#\n")
        f.write("# 碼表各字段以製表符（Tab）分隔\n")
        f.write("# 順序爲：文字、編碼、權重（決定重碼的次序、可選）\n")
        f.write("#\n")
        f.write("# no comment\n")
        for word, shortcut, weight in entries:
            f.write(f"{word}\t{shortcut}\t{weight}\n")

def main():
    parser = argparse.ArgumentParser(description="Gboard 词库转 Rime 格式，支持增量合并")
    parser.add_argument("input", nargs="?", default="dictionary.txt", help="Gboard 导出的词典文件")
    parser.add_argument("output", nargs="?", default="custom_phrase.txt", help="输出的 Rime 词库文件")
    parser.add_argument("--overwrite", action="store_true", help="覆盖模式（不合并，直接覆盖输出文件）")
    parser.add_argument("--merge", action="store_true", help="合并模式（默认行为，与 --overwrite 互斥）")
    args = parser.parse_args()

    # 确定模式：如果指定 --overwrite 则覆盖，否则合并（默认）
    overwrite = args.overwrite
    if args.merge:
        overwrite = False

    from pathlib import Path
    output_path = Path(args.output)

    # 解析新 Gboard 文件
    new_entries = parse_gboard(args.input)
    if not new_entries:
        print("未找到任何有效条目，请检查输入文件格式。")
        sys.exit(1)

    if overwrite or not output_path.exists():
        # 覆盖模式或输出文件不存在：直接生成新文件
        # 需要为新条目分配权重（按顺序，同码权重递增）
        from collections import defaultdict
        counter = defaultdict(int)
        weighted_entries = []
        for shortcut, word in new_entries:
            counter[shortcut] += 1
            weight = counter[shortcut]
            weighted_entries.append((word, shortcut, weight))
        write_rime_file(weighted_entries, output_path)
        print(f"覆盖写入完成！共处理 {len(weighted_entries)} 条短语。")
    else:
        # 合并模式：读取已有文件，合并新条目
        existing_entries, existing_max_weight = parse_existing_rime(output_path)
        merged = merge_entries(new_entries, existing_entries, existing_max_weight)
        write_rime_file(merged, output_path)
        added = len(merged) - len(existing_entries)
        print(f"合并完成！原有 {len(existing_entries)} 条，新增 {added} 条，总计 {len(merged)} 条。")

    print(f"输出文件: {output_path}")
    print("请将此文件复制到 ~/.config/ibus/rime/custom_phrase.txt 并重新部署 Rime。")

if __name__ == "__main__":
    main()