---
name: academic-workshop
description: >
  组会PPT全流程制作Skill——从论文深读/文献解读到PPTX导出的一站式流水线。
  融合ppt-master的确定性工厂哲学与花叔Design的审美工作室哲学，
  支持用户PPT模板解剖、品味守卫反slop扫描、组会Q&A防御生成。
  触发词：组会PPT、学术汇报PPT、论文汇报PPT、文献PPT、组会汇报、学术报告PPT、
  seminar PPT、group meeting PPT、做组会PPT、做汇报PPT、学术工坊
---

# 学术工坊 · 组会PPT Skill

> **定位**：ppt-master(工厂哲学) + 花叔Design(工作室哲学) 的精准杂交
> **核心公式**：工厂骨架(确定性) + 工作室品味(审美) = 学术工坊
> **目标产出**：组会汇报PPT（PPTX原生格式），兼顾学术严谨性与视觉品味

---

## 触发规则

- 用户说"做组会PPT"/"汇报PPT"/"组会汇报"/"文献PPT"等 → 直接激活
- 用户给了一个PPTX模板并说要组会PPT → 激活+走模板解剖路线
- 用户只给了论文/文献内容 → 激活+走自由设计路线

---

## 全局执行纪律（8条铁律）

> 🚨 以下规则凌驾所有流程，违反任何一条 = 执行失败：

1. **串行执行** — 步骤按序执行；每步输出是下步输入
2. **⛔ BLOCKING = 硬停** — 标⛔的步骤必须完整停下，等用户明确回复后才能继续
3. **禁止跨阶段打包** — Step 4八项确认是⛔ BLOCKING，确认后所有后续步骤自动推进
4. **门前验证** — 每步开头有🚧 GATE，必须验证前提才能开始
5. **禁止投机执行** — 禁止在当前步骤预写后续步骤内容
6. **禁止子代理SVG** — Step 6 SVG生成由主代理端到端完成
7. **逐页生成** — SVG页逐页顺序生成，禁止批量
8. **spec_lock每页重读** — 每页SVG生成前必须`read_file <project_path>/spec_lock.md`

---

## Windows执行规范（🔴必读）

> 🪟 Windows环境下必须遵守以下规范，否则脚本会静默失败或编码崩溃：

### Python路径

```
PYTHON = C:\Users\叶泳峰\.workbuddy\binaries\python\envs\default\Scripts\python.exe
```

### 执行方式

**禁止**用 `& python` 或 `python -c "..."` 直接执行，**必须**用 `Start-Process + 重定向`：

```powershell
$python = "C:\Users\叶泳峰\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
$script = "${SKILL_DIR}/scripts/<script_name>.py"
Start-Process -FilePath $python -ArgumentList "`"$script`" <args>" `
  -NoNewWindow -Wait -PassThru `
  -RedirectStandardOutput "$env:TEMP\aw_out.txt" `
  -RedirectStandardError "$env:TEMP\aw_err.txt"
Get-Content "$env:TEMP\aw_out.txt"
Get-Content "$env:TEMP\aw_err.txt"
```

原因：PowerShell管道编码(UTF-16)与Python stdout(UTF-8)不匹配，`& python` 输出不可见。

### 项目路径

**推荐**在A盘创建项目（`A:\claudeworks\` 无中文字符），避免C扩展DLL加载失败。
如果必须在C盘含中文路径下运行，`win_compat.py` 已自动处理 `sys.path` 修复。

### 编码

所有Python脚本入口已内置 `win_compat.py`，自动将 stdout/stderr 切换为 UTF-8。
代码中**禁止** `print()` 使用emoji字符（用ASCII替代，如 `[OK]` `[WARN]` `[ERR]`）。

---

## 8步流水线

### Step 1：输入接收

🚧 **GATE**：用户提供了源材料（论文PDF/URL/Markdown/已解读内容）

**1.1 判断输入类型** → 选择对应转换脚本：

| 用户提供 | 执行命令 |
|---------|---------|
| 论文PDF | `python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| Word/DOCX | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| 网页URL | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| Excel/XLSX | `python3 ${SKILL_DIR}/scripts/source_to_md/excel_to_md.py <file>` |
| Markdown | 直接读取 |
| 已有深读笔记 | 直接读取深读产出 |

> 🤖 **自动检测**：如果用户只给了文件路径而未指定类型，检测文件扩展名自动路由到对应脚本。`.pdf` → pdf_to_md，`.docx` → doc_to_md，`.xlsx/.csv` → excel_to_md。

> ⚡ 衔接paper-deep-read-v3：如果用户刚跑过深读，读取其产出目录的笔记作为源内容。

**1.2 检测PPTX模板** → 扫描用户消息中的`.pptx`文件路径，有则记录`template_path`变量。

**1.3 提取论文图片**（PDF路线时）：`pdf_to_md.py`已自动提取图片。

> 📸 **图片命名**：提取的图片默认按页面顺序命名。如需对应论文Figure编号，请在深读阶段用 `paper-deep-read-v3` 的图片提取功能（自动识别Figure caption并重命名为 `fig1.png`/`fig2.png`）。

✅ 源内容就绪，自动进入Step 2。

---

### Step 2：项目初始化

🚧 **GATE**：Step 1完成

**2.1 创建项目目录**：
```bash
python3 ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format ppt169
```

**2.2 导入源内容**：
```bash
python3 ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move
```

**2.3 创建学术工坊额外目录**：
```bash
mkdir <project_path>/template_elements
mkdir <project_path>/notes
```

✅ 项目结构就绪，进入Step 3。

---

### Step 3：模板解剖（条件触发）

🚧 **GATE**：Step 2完成

**触发条件**：`template_path`变量已设置（用户提供了PPTX文件）

无模板 → 直接进入Step 4自由设计路线。

**3.1 匹配模板**（如果用户说的是风格名）：
```bash
cat ${SKILL_DIR}/templates/layouts/layouts_index.json
```

**3.2 复制模板SVG到项目**：
```bash
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.svg <project_path>/templates/
```

**3.3 运行模板解剖器** ⭐：
```bash
python3 ${SKILL_DIR}/scripts/template_dissector.py <pptx_path> <project_path>
```

解剖器产出6类JSON：
| 元素类别 | 输出文件 |
|---------|---------|
| 色值组 | `template_elements/color_palette.json` |
| 字体组 | `template_elements/font_groups.json` |
| 布局骨架 | `template_elements/layout_skeletons.json` |
| 装饰元素 | `template_elements/decorations.json` |
| 图文占位 | `template_elements/placeholders.json` |
| 节奏映射 | `template_elements/rhythm_map.json` |

**3.4** 解剖器自动合入`spec_lock.md` + `design_spec.md`

✅ 模板解剖完成（或跳过），进入Step 4。

---

### Step 4：八项确认 ⛔ BLOCKING

🚧 **GATE**：Step 3完成

⛔ **硬停**：确认后所有后续步骤自动推进。

**4.1** 读取角色定义：
```
Read references/strategist.md
Read templates/design_spec_reference.md
```

**4.2** 读取模板参考（模板路线时）：读取6个解剖JSON

**4.3** 分析源内容 → 提取八项确认所需信息

**4.4** 图片分析（如有图片）：
```bash
python3 ${SKILL_DIR}/scripts/analyze_images.py <project_path>/images
```

**4.5** 读取风格参考（可选）：
```
Read references/design-styles-excerpt.md
```

**4.6** 八项确认清单 → 向用户呈现，等待确认：

| # | 确认项 | 自由设计默认 |
|---|--------|------------|
| 1 | 画布格式 | ppt169(16:9) |
| 2 | 页数范围 | 8-12页 |
| 3 | 目标受众 | 导师+同组成员 |
| 4 | 风格目标 | 简洁专业+视觉叙事 |
| 5 | 色值方案 | 低饱和蓝#003366系+中性灰 |
| 6 | 图标使用 | tabler-outline |
| 7 | 字体方案 | Source Serif+Microsoft YaHei+Consolas |
| 8 | 图片使用 ⭐ | 关键结果页嵌入原图 |

**4.7** 产出`design_spec.md`（人类可读设计叙事）

**4.8** 产出`spec_lock.md`（机器可读执行锁）

✅ 八项确认完成。⛔ 解封，后续步骤自动推进。

---

### Step 5：品味守卫 ⭐

🚧 **GATE**：Step 4完成

**5.1** 读取品味规则：
```
Read references/taste_guardian.md
```

**5.2** AI品味扫描 — 对照10条规则扫描design_spec.md：

| # | 扫描项 | 判定 |
|---|--------|------|
| 1 | 紫渐变 | 🔴禁止 |
| 2 | Emoji图标 | 🔴禁止 |
| 3 | 圆角卡片+左border | 🟡警告 |
| 4 | 均匀卡片网格 | 🔴禁止 |
| 5 | CSS剪影代替真实图 | 🔴禁止 |
| 6 | Inter/Roboto主字体 | 🟡警告 |
| 7 | 装饰性icon泛滥 | 🟡警告 |
| 8 | 信息密度过高 | 🟡警告 |
| 9 | 渐变背景 | 🔴禁止 |
| 10 | 花哨动画暗示 | 🟡警告 |

**5.3** 产出`<project_path>/taste_report.md`

**5.4** 修复执行：🔴必须修复→修改design_spec+spec_lock → 重扫直到0个🔴

**5.5** 机器辅助检测（可选）：
```bash
python3 ${SKILL_DIR}/scripts/taste_guardian_cli.py <project_path>/design_spec.md
```

✅ 品味守卫通过（0个🔴禁止项），进入Step 6。

---

### Step 6：逐页SVG生成

🚧 **GATE**：Step 5完成

**6.1** 读取角色定义：
```
Read references/executor-base.md
Read references/shared-standards.md
Read references/executor-academic.md
```

**6.2** 设计参数确认（强制）：输出画布/色值/字体/字号参数

**6.3** 逐页SVG生成循环 — 每页3步：

**6.3.1** 重读spec_lock（强制）
**6.3.2** 查节奏标签 → 执行对应布局纪律：

| 标签 | 布局纪律 |
|------|---------|
| `anchor` | 结构页(封面/章节/结尾)，模板路线时继承模板骨架 |
| `dense` | 信息密集页，允许卡片网格/多列/表格 |
| `breathing` | 留白冲击页，禁止多卡片网格，用大图+浮动标题 |

**6.3.3** 学术页面类型规则：

| 页面类型 | 节奏 | SVG命名 |
|---------|------|---------|
| 封面 | anchor | P01_cover.svg |
| 研究背景 | dense | P02_background.svg |
| 方法流程 | dense | P03_method.svg |
| 关键结果 | breathing | P04_results.svg |
| 讨论局限 | dense | P05_discussion.svg |
| 总结展望 | anchor | P06_summary.svg |
| 致谢页 | anchor | P07_thanks.svg |

**6.4** SVG产出 → `svg_output/`

**6.5** 图表校验（条件触发）：
```bash
python3 ${SKILL_DIR}/scripts/svg_position_calculator.py <project_path>
```

**6.6** 质量检查门（强制）：
```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>
```

✅ 所有SVG生成+质量检查通过，进入Step 7。

---

### Step 7：逐字稿 + Q&A防御 ⭐

🚧 **GATE**：Step 6完成

**7.1** 逐字稿生成 → `notes/total.md`（口语化，每页一段）

> 📅 日期占位符：在逐字稿中使用 `{{DATE}}` 或 `{{DATE_CN}}` 代替具体日期，`total_md_split.py` 拆分时会自动替换为当天日期（如 `2026年05月05日`）。也可用 `{{DATE_EN}}` 获得英文格式（`2026-05-05`）。

**7.2** Q&A防御生成 → `notes/qa_defense.md`

读取：`Read references/qa_defense.md`

AI模拟导师视角，每页3-5个追问+防御回答。

> ⚡ 衔接qa-defense-system：如果用户已跑过，读取产出合并。

✅ 逐字稿+Q&A完成，进入Step 8。

---

### Step 8：后处理 & PPTX导出

🚧 **GATE**：Step 7完成

**三步顺序执行**（禁止合并为单命令）：

**8.1** 逐字稿拆分：
```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**8.2** SVG后处理：
```bash
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

**8.3** PPTX导出：
```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
```

产出：
- `output/<name>_<timestamp>.pptx` — 主PPTX（原生DrawingML）
- `output/<name>_svg.pptx` — SVG预览PPTX

**可选 8.4** TTS音频：
```bash
python3 ${SKILL_DIR}/scripts/notes_to_audio.py <project_path> --backend edge
```

✅ PPTX导出完成，流水线结束。

---

## 与现有Skill生态的衔接

| 衔接Skill | 衔接点 | 方式 |
|-----------|--------|------|
| paper-deep-read-v3 | Step 1源内容 | 读取深读笔记 |
| qa-defense-system | Step 7 Q&A | 读取产出合并 |
| group-meeting-pipeline | 整体 | PPT制作环节 |
| ppt-master | scripts/templates/references | 整目录复用 |
| 花叔Design | 反slop/风格/动画/PPTX约束 | 蒸馏为5个reference |

---

## 文件结构

```
~/.workbuddy/skills/academic-workshop/
├── SKILL.md                     # 本文件
├── requirements.txt             # Python依赖
├── scripts/                     # ppt-master整目录复用 + 2个新脚本
│   ├── template_dissector.py     # ⭐ 模板解剖器
│   ├── taste_guardian_cli.py     # ⭐ 品味守卫CLI
│   └── ...（22个顶层.py + 10个子目录）
├── references/
│   ├── strategist.md             # ⭐ 学术策略师
│   ├── executor-base.md          # ⭐ 学术执行器基础
│   ├── executor-academic.md      # ⭐ 学术风格专属
│   ├── taste_guardian.md         # ⭐ 品味守卫规则
│   ├── qa_defense.md             # ⭐ Q&A防御角色
│   ├── design-styles-excerpt.md  # ⭐ 学术5种风格
│   ├── anti-slop-checklist.md    # ⭐ 反AI slop清单
│   ├── animation-restraint.md    # ⭐ 动画克制规则
│   ├── editable-pptx-rules.md    # ⭐ PPTX导出4约束
│   ├── gallery-showcase-excerpt.md # ⭐ 结果页展示风格
│   └── ...（ppt-master 14个reference）
├── templates/
│   ├── design_spec_reference.md  # ⭐ 八项确认模板
│   ├── spec_lock_reference.md    # spec锁模板
│   ├── layouts/                  # 21套+浙大蓝
│   ├── charts/                   # 73图表
│   └── icons/                    # 5库11631图标
├── workflows/
│   ├── dissect-template.md       # ⭐ 模板解剖workflow
│   └── ...（ppt-master 5个workflow）
├── docs/
│   ├── faq.md                    # ⭐ 常见问题
│   └── CHANGES.md               # ⭐ 变更日志
└── inherited_from/
    ├── ppt_master_asset_map.md
    └── huashu_design_asset_map.md
```
