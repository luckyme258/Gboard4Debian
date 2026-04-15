#!/usr/bin/env python3
"""
Rime 自定义短语管理器 - 便携版
- 默认在脚本所在目录下读取/保存 custom_phrase.txt
- 支持增删改查、导入 Gboard 词库、自动权重
"""

import os
import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import defaultdict
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_FILE = SCRIPT_DIR / "custom_phrase.txt"

class PhraseManager:
    def __init__(self, root, filepath=None):
        self.root = root
        self.root.title("Rime 自定义短语管理器 (便携版)")
        self.root.geometry("850x550")
        # 如果未指定文件，使用脚本目录下的 custom_phrase.txt
        self.filepath = filepath or DEFAULT_FILE
        self.phrases = []          # 存储 (text, code, weight)
        self.filtered = []         # 过滤后的列表
        self.search_var = tk.StringVar()
        self.setup_ui()
        self.load_file()
    
    def setup_ui(self):
        # 工具栏
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(toolbar, text="搜索:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(toolbar, text="添加", command=self.add_phrase).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="删除", command=self.delete_phrase).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="导入 Gboard", command=self.import_gboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="保存", command=self.save_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="另存为...", command=self.save_as).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="打开文件夹", command=self.open_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="刷新", command=self.refresh_display).pack(side=tk.LEFT, padx=5)
        
        # 显示当前文件路径
        self.path_label = ttk.Label(self.root, text=f"当前词库文件: {self.filepath}", relief=tk.SUNKEN, anchor=tk.W)
        self.path_label.pack(fill=tk.X, side=tk.TOP, padx=5, pady=2)
        
        # 表格
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("文字", "编码", "权重")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("文字", text="文字")
        self.tree.heading("编码", text="编码")
        self.tree.heading("权重", text="权重")
        self.tree.column("文字", width=350)
        self.tree.column("编码", width=150)
        self.tree.column("权重", width=80)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", self.edit_phrase)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self.edit_phrase)
        self.context_menu.add_command(label="删除", command=self.delete_phrase)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 底部状态栏
        self.status = ttk.Label(self.root, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
    
    def load_file(self):
        """加载 custom_phrase.txt 到内存"""
        self.phrases = []
        if not self.filepath.exists():
            self.status.config(text=f"文件不存在，将创建新文件: {self.filepath}")
            self.refresh_display()
            return
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip('\n')
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        text = parts[0].strip()
                        code = parts[1].strip()
                        try:
                            weight = int(parts[2].strip())
                        except:
                            weight = 1
                        self.phrases.append((text, code, weight))
            self.status.config(text=f"已加载 {len(self.phrases)} 条短语")
        except Exception as e:
            messagebox.showerror("加载失败", f"无法读取文件：{e}")
        self.refresh_display()
    
    def refresh_display(self):
        search_text = self.search_var.get().strip().lower()
        if search_text:
            self.filtered = [p for p in self.phrases if search_text in p[0].lower() or search_text in p[1].lower()]
        else:
            self.filtered = self.phrases.copy()
        self.update_tree()
        self.status.config(text=f"显示 {len(self.filtered)} / {len(self.phrases)} 条")
    
    def update_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for text, code, weight in self.filtered:
            self.tree.insert("", tk.END, values=(text, code, weight))
    
    def on_search(self, event=None):
        self.refresh_display()
    
    def add_phrase(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加短语")
        dialog.geometry("400x220")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="文字:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        text_entry = ttk.Entry(dialog, width=40)
        text_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="编码:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        code_entry = ttk.Entry(dialog, width=40)
        code_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def get_auto_weight(code):
            max_w = 0
            for _, c, w in self.phrases:
                if c == code and w > max_w:
                    max_w = w
            return max_w + 1
        
        weight_var = tk.IntVar()
        ttk.Label(dialog, text="权重:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        weight_spin = ttk.Spinbox(dialog, from_=1, to=9999, textvariable=weight_var, width=10)
        weight_spin.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        def on_code_change(*args):
            code = code_entry.get().strip()
            if code:
                weight_var.set(get_auto_weight(code))
        code_entry.bind("<KeyRelease>", on_code_change)
        
        def save():
            text = text_entry.get().strip()
            code = code_entry.get().strip()
            if not text or not code:
                messagebox.showerror("错误", "文字和编码不能为空")
                return
            for t, c, w in self.phrases:
                if t == text and c == code:
                    messagebox.showerror("错误", f"短语 '{text}' 与编码 '{code}' 已存在")
                    return
            weight = weight_var.get()
            self.phrases.append((text, code, weight))
            self.refresh_display()
            dialog.destroy()
        
        ttk.Button(dialog, text="确定", command=save).grid(row=3, column=0, pady=10)
        ttk.Button(dialog, text="取消", command=dialog.destroy).grid(row=3, column=1, pady=10)
    
    def edit_phrase(self, event=None):
        # 获取选中的项目（兼容双击和右键）
        item = self.tree.focus()
        if not item and event:
            item = self.tree.identify_row(event.y)
        if not item:
            sel = self.tree.selection()
            if sel:
                item = sel[0]
            else:
                return
        values = self.tree.item(item, "values")
        if not values or len(values) < 3:
            return
        old_text, old_code, old_weight = values[0], values[1], int(values[2])
        
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑短语")
        dialog.geometry("400x220")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="文字:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        text_entry = ttk.Entry(dialog, width=40)
        text_entry.insert(0, old_text)
        text_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="编码:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        code_entry = ttk.Entry(dialog, width=40)
        code_entry.insert(0, old_code)
        code_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="权重:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        weight_spin = ttk.Spinbox(dialog, from_=1, to=9999, width=10)
        weight_spin.insert(0, str(old_weight))
        weight_spin.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        def save():
            new_text = text_entry.get().strip()
            new_code = code_entry.get().strip()
            if not new_text or not new_code:
                messagebox.showerror("错误", "文字和编码不能为空")
                return
            for t, c, w in self.phrases:
                if (t == new_text and c == new_code) and not (t == old_text and c == old_code):
                    messagebox.showerror("错误", f"短语 '{new_text}' 与编码 '{new_code}' 已存在")
                    return
            new_weight = int(weight_spin.get())
            for i, (t, c, w) in enumerate(self.phrases):
                if t == old_text and c == old_code and w == old_weight:
                    self.phrases[i] = (new_text, new_code, new_weight)
                    break
            self.refresh_display()
            dialog.destroy()
        
        ttk.Button(dialog, text="确定", command=save).grid(row=3, column=0, pady=10)
        ttk.Button(dialog, text="取消", command=dialog.destroy).grid(row=3, column=1, pady=10)
    
    def delete_phrase(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, "values")
        if not values:
            return
        text, code, weight = values[0], values[1], int(values[2])
        if messagebox.askyesno("确认删除", f"确定要删除 '{text}' ({code}) 吗？"):
            for i, (t, c, w) in enumerate(self.phrases):
                if t == text and c == code and w == weight:
                    del self.phrases[i]
                    break
            self.refresh_display()
    
    def import_gboard(self):
        filepath = filedialog.askopenfilename(
            title="选择 Gboard 导出的文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
        new_entries = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    code = parts[0].strip()
                    word = parts[1].strip()
                    word = re.sub(r'\s*(zh-CN|zh-TW|zh-HK|en-US|ja-JP)\s*$', '', word, flags=re.IGNORECASE)
                    word = word.split()[0] if word.split() else word
                    if code and word:
                        new_entries.append((code, word))
        if not new_entries:
            messagebox.showwarning("警告", "未从文件中解析到有效条目")
            return
        
        existing_set = {(c, t) for t, c, w in self.phrases}
        max_weight = defaultdict(int)
        for t, c, w in self.phrases:
            if w > max_weight[c]:
                max_weight[c] = w
        added = 0
        for code, word in new_entries:
            if (code, word) in existing_set:
                continue
            max_weight[code] += 1
            weight = max_weight[code]
            self.phrases.append((word, code, weight))
            existing_set.add((code, word))
            added += 1
        self.refresh_display()
        messagebox.showinfo("导入完成", f"成功导入 {added} 条新短语")
    
    def save_file(self):
        """保存到当前文件路径（脚本目录下的 custom_phrase.txt）"""
        try:
            # 确保目录存在
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            # 备份旧文件
            if self.filepath.exists():
                backup = self.filepath.with_suffix(".txt.bak")
                import shutil
                shutil.copy(self.filepath, backup)
            # 写入新内容
            with open(self.filepath, 'w', encoding='utf-8') as f:
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
                # 按权重降序排列（权重大的优先）
                sorted_phrases = sorted(self.phrases, key=lambda x: x[2], reverse=True)
                for text, code, weight in sorted_phrases:
                    f.write(f"{text}\t{code}\t{weight}\n")
            self.status.config(text=f"已保存到 {self.filepath}")
            messagebox.showinfo("保存成功", f"已保存 {len(self.phrases)} 条短语到\n{self.filepath}")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存文件：{str(e)}")
            self.status.config(text=f"保存失败: {e}")
    
    def save_as(self):
        """另存为其他文件"""
        new_path = filedialog.asksaveasfilename(
            title="另存为",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not new_path:
            return
        old_path = self.filepath
        self.filepath = Path(new_path)
        self.save_file()
        self.path_label.config(text=f"当前词库文件: {self.filepath}")
        # 询问是否切换工作文件
        if messagebox.askyesno("切换文件", f"已保存到 {self.filepath}\n是否将此文件作为当前工作文件？"):
            pass  # 已经切换
        else:
            self.filepath = old_path
            self.path_label.config(text=f"当前词库文件: {self.filepath}")
    
    def open_folder(self):
        """打开脚本所在目录（即 custom_phrase.txt 所在目录）"""
        import subprocess
        subprocess.run(["xdg-open", str(SCRIPT_DIR)])
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

def main():
    root = tk.Tk()
    app = PhraseManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()