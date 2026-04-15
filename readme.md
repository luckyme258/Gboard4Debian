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

感谢你的验证！你说得对，Gboard 的个人词典导入功能**可以直接选择 `.txt` 文件**，不需要打包成 ZIP。之前的经验可能是特定版本或操作方式导致的误解。

现在更新 `README.md` 中的相关说明，去掉 ZIP 步骤，改为直接传输 `.txt` 文件。

---

## 📱 如何让 Gboard 使用最新的词典

通过 `rime2gboard.py` 脚本，将 Linux 上的 Rime 词库转换为 Gboard 支持的 `.txt` 文件，直接导入手机。

### 🔄 同步流程

```mermaid
flowchart LR
    A[Linux 电脑<br>Rime 词库] -->|`rime2gboard.py`| B[Gboard 格式<br>dictionary666.txt]
    B -->|传输| C[Android 手机]
    C -->|Gboard 导入| D[Gboard 使用最新词典]
```

### ⚙️ 详细操作步骤

1. **导出词库**  
   在项目目录下运行：
   ```bash
   python3 rime2gboard.py
   ```
   生成 `dictionary666.txt`（UTF-8 编码，制表符分隔）。

2. **传输到手机**  
   通过数据线、蓝牙、网盘等方式将 `dictionary666.txt` 文件复制到手机上。

3. **导入 Gboard**  
   - 手机设置 → 语言和输入法 → 虚拟键盘 → Gboard  
   - 词典 → 个人词典 → 选择语言（如“中文（简体）”）  
   - 点击右上角菜单 → **导入** → 选择 `dictionary666.txt`  
   - 完成。

### ✅ 验证

在任意输入框输入快捷码（如 `mge`），候选词中出现 `M哥` 即表示成功。

---

## 📌 注意事项

- 文件必须是 **UTF-8 编码**，避免乱码。
- 列分隔符必须为 **制表符（Tab）**，不能是空格。
- 每行需包含语言标签 `zh-CN`（脚本已自动添加）。
- 如果导入失败，检查文件编码和分隔符是否正确。

---

