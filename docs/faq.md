# 学术工坊 FAQ

---

## 基本使用

### Q: 如何使用浙大蓝模板？

在Step 1时说"用浙大蓝模板"或"zju_blue"，系统会自动匹配到`templates/layouts/zju_blue/`目录。如果你有浙大的PPTX模板文件，也可以直接提供文件路径，系统会运行模板解剖器提取设计基因。

浙大蓝模板的主色是`#003F88`，accent色是`#ED7D31`（橙），字体是思源黑体 CN系列。

### Q: 如何引用论文Figure？

在Step 4八项确认的第8项"图片使用"中，选择"嵌入原图"。系统会在Step 1.3自动提取PDF中的图片到`images/`目录。在Step 6 SVG生成时，直接引用图片路径：

```svg
<image href="images/figure3a.png" x="100" y="80" width="480" height="360" 
       preserveAspectRatio="xMidYMid meet"/>
```

**禁止**用AI生成图替代论文原图——这是品味守卫的硬规则。

### Q: 品味守卫报了🔴禁止项怎么办？

🔴禁止项**必须修复**才能继续到Step 6。常见修复：

| 🔴禁止项 | 修复方法 |
|---------|---------|
| 紫渐变 | 替换为低饱和蓝（#003366/#003F88）或中性色 |
| Emoji图标 | 改为tabler-outline图标库或无图标 |
| 均匀卡片网格 | 在dense页之间插入breathing页（大图+留白） |
| CSS剪影/SVG手画 | 改用论文原图或诚实placeholder（灰块+标注） |
| 渐变背景 | 改为纯色（#FFFFFF/#F8F8F8），仅封面允许渐变 |

修复后重新扫描，直到0个🔴。

---

## Skill衔接

### Q: 如何衔接paper-deep-read-v3？

如果用户刚跑过paper-deep-read-v3深读，学术工坊在Step 1会直接读取深读笔记作为源内容，跳过格式转换步骤。深读产出目录通常包含：
- 深读笔记.md（结构化内容）
- 图片文件（论文Figure）

### Q: 如何衔接qa-defense-system？

如果用户已跑过qa-defense-system，学术工坊在Step 7会读取其Q&A产出合并到`notes/qa_defense.md`。如果没有，学术工坊会根据`references/qa_defense.md`指导AI自行生成。

### Q: 如何使用TTS音频？

在Step 8完成后，可选执行Step 8.4：
```bash
python3 ${SKILL_DIR}/scripts/notes_to_audio.py <project_path> --backend edge --voice zh-CN-XiaoxiaoNeural
```
默认使用edge-tts（免费），还支持5个云TTS后端。

### Q: 如何使用可视化编辑？

```bash
python3 ${SKILL_DIR}/scripts/svg_editor/server.py <project_path>
```
浏览器打开后，可以标注SVG中的问题区域，AI根据标注修复SVG。

---

## 技术问题

### Q: Python路径含中文导致报错怎么办？

使用绝对路径调用Python：
```bash
C:\Users\叶泳峰\.workbuddy\binaries\python\versions\3.13.12\python.exe <script>
```
如果pymupdf因中文路径import失败，用`sys.path.insert(0, site_packages)`或以脚本文件方式执行。

### Q: PowerShell中看不到Python输出怎么办？

这是环境已知问题。解决方案：让脚本写文件输出，然后用Read工具读取。

### Q: 支持哪些PPTX模板？

学术工坊内置24套模板（继承自ppt-master），学术相关推荐：
- `academic_defense` — 通用学术答辩
- `zju_blue` — 浙大蓝组会
- `medical_university` — 医学院
- `重庆大学` — 重庆大学专属

也可提供任意PPTX文件，解剖器会自动提取设计基因。
