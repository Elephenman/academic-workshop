# 花叔Design 资产溯源对照表

> 记录学术工坊从花叔Design蒸馏的每份资产的原始路径、蒸馏日期、蒸馏方式

**蒸馏日期**：2026-05-04
**花叔Design安装路径**：`~/.workbuddy/skills/huashu-design/`
**学术工坊安装路径**：`~/.workbuddy/skills/academic-workshop/`

---

## 蒸馏产出

| 蒸馏产出 | 源文件 | 蒸馏方式 | 学术适配内容 |
|---------|--------|---------|-------------|
| `references/design-styles-excerpt.md` | `references/design-styles.md` | 只保留5种学术适配★★★风格 | 增加学术适配说明+风格选择指南表 |
| `references/anti-slop-checklist.md` | `SKILL.md` §6.2 | 提取反slop清单核心 | 增加5条学术禁止项(紫渐变/Emoji/均匀网格/CSS剪影/渐变背景) |
| `references/animation-restraint.md` | `references/animation-best-practices.md` + `animation-pitfalls.md` | 蒸馏为学术克制版 | 学术场景=几乎不用动画，仅fade切换；保留设计思维(节奏/层级/留白/克制) |
| `references/editable-pptx-rules.md` | `references/editable-pptx.md` | 提取4条硬约束 | 增加SVG→DrawingML路线说明+学术5条特别提醒 |
| `references/gallery-showcase-excerpt.md` | `references/apple-gallery-showcase.md` | 蒸馏结果页展示风格 | 删除3D倾斜/动画/画廊模式，保留大图+解读视觉Token+3种布局模式 |

---

## 不复用的花叔Design资产（及原因）

| 被排除资产 | 原因 |
|-----------|------|
| `scripts/html2pptx.js` | 学术工坊走SVG→DrawingML路线，更成熟稳定 |
| `scripts/export_deck_pptx.mjs` | 同上 |
| `scripts/export_deck_pdf.mjs` | 同上 |
| `scripts/render-video.js` | 组会PPT不需要视频导出 |
| `scripts/convert-formats.sh` | 同上 |
| `scripts/add-music.sh` | 同上 |
| `assets/deck_index.html` | ppt-master有自己的项目管理 |
| `assets/deck_stage.js` | 同上 |
| `assets/animations.jsx` | 学术PPT几乎不用动画 |
| `assets/ios_frame.jsx` | 非App原型场景 |
| `assets/android_frame.jsx` | 同上 |
| `assets/macos_window.jsx` | 同上 |
| `assets/browser_window.jsx` | 同上 |
| `assets/design_canvas.jsx` | 学术工坊不走variations模式 |
| `references/workflow.md` | 学术工坊有自己的9步流水线 |
| `references/react-setup.md` | 不用React |
| `references/content-guidelines.md` | 学术内容规范不同 |
| `references/slide-decks.md` | ppt-master有完整PPT制作流程 |
| `references/verification.md` | ppt-master有质量检查 |
| `references/tweaks-system.md` | 学术工坊不走Tweaks模式 |
| `references/scene-templates.md` | 学术场景模板不同 |
| `references/critique-guide.md` | 学术工坊用品味守卫替代 |
| `references/sfx-library.md` | 不需要音效 |
| `references/audio-design-rules.md` | 不需要音频 |
| `references/video-export.md` | 不需要视频导出 |
| `references/animation-pitfalls.md` | 已蒸馏入animation-restraint.md |
| `references/animations.md` | 同上 |
| `SKILL.md`（主体） | 学术工坊有独立SKILL.md |
| `README.md` | 非功能性 |
