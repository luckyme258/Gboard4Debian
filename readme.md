基于我们在 Debian 上的实践，总结出一套**从 Gboard 到 Rime 的词库管理方案**，核心是 **自定义短语 + 双向转换 + GUI 管理**。

---

## 🔧 使用到的框架与软件

| 组件 | 名称 | 作用 |
|------|------|------|
| 输入法框架 | **IBus** + **ibus-rime** | 提供 Rime 输入法引擎 |
| 词库格式 | `custom_phrase.txt` | Rime 的自定义短语文件（Tab 分隔：文字、编码、权重） |
| 转换脚本 | `gboard2rime.py` | 将 Gboard 导出的 `dictionary.txt` 转为 Rime 格式 |
| 反向转换 | `rime2gboard.py` | 将 Rime 词库转回 Gboard 可导入的 TSV |
| GUI 管理 | `rime_phrase_manager.py` | 图形化增删改查、导入 Gboard、自动权重 |
| 版本控制 | `git` | 管理词库迭代 |

---

## 📦 安装与配置（Debian）

```bash
# 安装 Rime 输入法（仅核心拼音方案）
sudo apt install ibus-rime rime-data-luna-pinyin

# 重启 IBus 并添加输入法
ibus-daemon -drx
# 然后在系统设置中添加“中文（Rime）”
```

---

## 🗂️ 目录结构（示例）

```
~/文档/Gboard4Debian/
├── custom_phrase.txt          # 当前生效的 Rime 词库
├── dictionary.txt             # 从 Gboard 导出的原始文件
├── gboard2rime.py             # 转换脚本（Gboard → Rime）
├── rime2gboard.py             # 转换脚本（Rime → Gboard）
├── rime_phrase_manager.py     # GUI 管理器
└── readme.md                  # 说明文档
```

---

## ✍️ 操作方法

### 1. 从 Gboard 导出词库
- 手机 Gboard → 个人词典 → 导出 → 得到 `dictionary.txt`
- 传到电脑，放入项目目录

### 2. 转换为 Rime 格式
```bash
python3 gboard2rime.py dictionary.txt custom_phrase.txt
```
- 自动处理重复编码、清理语言标签、分配权重

### 3. 部署到 Rime
```bash
cp custom_phrase.txt ~/.config/ibus/rime/
```
- 右键 Rime 图标 → **重新部署**

### 4. 图形化管理词库
```bash
python3 rime_phrase_manager.py
```
- 表格展示，支持添加、删除、编辑、搜索
- 导入 Gboard 文件（增量合并）
- 保存后生成 `custom_phrase.txt`

### 5. 反向导出给 Gboard
```bash
python3 rime2gboard.py custom_phrase.txt dictionary666.txt
```
- 生成的文件可直接导入手机 Gboard

### 6. 版本控制
```bash
git init
git add *.py custom_phrase.txt
git commit -m "初始词库"
git push
```

---

## ✅ 核心优势

- **双向同步**：手机 ↔ 电脑词库互转
- **完全离线**：所有工具本地运行
- **无需 root**：词库操作在用户目录
- **增量更新**：多次导入自动去重、权重递增
- **GUI 友好**：不用记命令，点一点就管理

---

## 📌 小贴士

- 自定义编码避免与真实拼音冲突（如用 `mge` 而不是 `maige`）
- 相同编码多个词，**权重越大越靠前**，可通过 GUI 调整
- 修改词库后务必 **重新部署 Rime** 才能生效

这套方案已在 Debian 13 (Wayland) 上稳定运行，完美复刻 Gboard 的快捷短语体验。