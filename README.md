# academic-workshop

组会 / 学术汇报 PPT 全流程制作 Skill —— 从论文或 Markdown 源文档到**可编辑 PPTX** 的一站式流水线。

融合 ppt-master 的「确定性工厂」哲学与花叔 Design 的「审美工作室」哲学，内置用户模板解剖、品味守卫（反 AI-slop）扫描、组会 Q&A 防御生成。

> 适用：WorkBuddy user-level skill，放置于 `~/.workbuddy/skills/academic-workshop/`。

---

## 核心能力

1. **MD 结构驱动，内容不再单薄**
   自动抽取源文档的标题层级作为骨架，必加 **Agenda（汇报路线）** 与 **章节分隔页**；结果页采用
   「实验目的 → 图意拆解（Panel A–D）→ 核心发现 → 逻辑衔接」四段式，
   让 PPT 严格镜像原文的逻辑分区，而不是每张图配三句泛泛 bullet。

2. **图表保真（原比例 + 落位正确）**
   图按 md 内链接位置落位；导出采用 `preserveAspectRatio="xMidYMid meet"` + 高度优先布局，
   **原宽高比无拉伸、无裁切**；幻灯片背景纯白。

3. **浙大蓝模板**
   内置 `templates/layouts/zju_blue`（主蓝 `#003F88`、强调蓝 `#2B6CB0`、橙 `#ED7D31`、浅蓝 `#EBF2FA`），
   含 70px 蓝色页眉带、key-message 核心发现条、章节分隔页与封面。

4. **段落级文本框（本仓库优化点）**
   SVG→PPTX 转换器新增 `data-wrap-w` 属性：一个逻辑段落 = 一个**可编辑文本框**（PowerPoint 按宽度自动换行），
   不再「一行一个文本框」。修复了原转换器把每个 `<tspan>` 拆成独立框、导致 PPT 里零散碎框的问题。

5. **更大正文、符合投影审美（本仓库优化点）**
   统一字号体系（画布 1280×720，1px = 0.75pt）：结果页正文 15pt、一般正文 13.5pt、页眉标题 22.5pt、
   bullet 14.25pt，留白与可读性显著优于旧版的 ~10pt。

---

## 工作流

```
源文档(md/pdf) → 抽取结构骨架 → 生成 SVG 页面 → svg_to_pptx.py 导出原生 PPTX(含演讲备注)
```

1. 读取角色定义：`references/executor-base.md`、`shared-standards.md`、`executor-academic.md`
   以及 `references/md_driven_content.md`（MD 结构驱动 · 内容密度准则，本仓库新增）。
2. 若有用户模板，先解剖其设计元素。
3. 生成 SVG 页面：源为 Markdown 时直接 `python scripts/md_to_svg.py <input.md> --out <project_dir>`（白底 + 浙大蓝装饰 + 段落级文本 + 图按原比例落位）；手搓 SVG 时按 `references/md_driven_content.md` §9 对齐。
4. 运行 `python scripts/svg_to_pptx.py <project_dir> --only native -f ppt169` 导出可编辑 PPTX。

---

## 目录结构

```
academic-workshop/
├── SKILL.md                      # 技能入口与流程编排
├── README.md                     # 本文件
├── scripts/
│   ├── svg_to_pptx/              # SVG → PPTX 转换器（含 data-wrap-w 段落文本优化）
│   ├── md_to_svg.py              # 【新增】通用 md → 学术PPT(SVG) 生成器（段落级/浙大蓝/图原比例）
│   ├── project_manager.py
│   └── update_spec.py
├── references/
│   ├── md_driven_content.md      # 【新增】MD 结构驱动 · 内容密度 · 排版美学准则
│   ├── design-styles-excerpt.md
│   ├── anti-slop-checklist.md
│   └── ...
├── templates/
│   └── layouts/zju_blue/         # 浙大蓝模板（cover / chapter / content / toc）
└── ...
```

---

## 本仓库相对 v0.5.0 的优化（v0.6.0）

| 项 | 改动 |
|---|---|
| 段落级文本 | `drawingml_elements.py` 的 `convert_text` 新增 `data-wrap-w` 支持：段落合并为单个文本框，子 `<tspan>`（无 x/y/dy）转为框内 `<a:br/>` 换行；legacy 单行模式补回 `<a:p>` 包裹与 `box_y` 赋值（修复文字变空 bug） |
| 内容密度准则 | 新增 `references/md_driven_content.md`，固化「Agenda + 章节分隔页 + 结果页四段式 + 背景卡片网格 + 方法表/步骤链」的默认做法，并接入 `SKILL.md` Step 6.1 阅读清单 |
| 字号体系 | 正文提升到 13.5–15pt、页眉 22.5pt，符合投影可读与留白审美 |
| 配色 | 改用内置 `zju_blue` 真实模板系统（主蓝 `#003F88`），不再手搓配色 |
| 通用生成器 | 新增 `scripts/md_to_svg.py`：任意论文 md → 一套符合上述准则的浙大蓝 SVG（分区镜像/Agenda/分隔页/结果四段式/表格/卡片），图按位置原比例落位、段落级文本框、`clean_md` 去标记；`references/md_driven_content.md` 补 §9 作为参考实现说明 |

---

## 安装 / 使用

作为 WorkBuddy 用户级 skill：将本目录置于 `~/.workbuddy/skills/academic-workshop/` 即可在对话中通过
`/academic-workshop` 或自然语言「做组会 PPT」触发。

导出命令示例：

```bash
python scripts/svg_to_pptx.py <your_project_dir> --only native -f ppt169 -t none -a none -o output/deck.pptx
```
