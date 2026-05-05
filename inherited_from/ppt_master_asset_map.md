# ppt-master 资产溯源对照表

> 记录学术工坊从ppt-master复用的每份资产的原始路径、拷贝日期、版本信息

**拷贝日期**：2026-05-04
**ppt-master版本**：v2.5.0 (hugohe3/ppt-master)
**ppt-master源仓库**：https://github.com/hugohe3/ppt-master
**ppt-master安装路径**：`~/.workbuddy/skills/ppt-master/`
**学术工坊安装路径**：`~/.workbuddy/skills/academic-workshop/`
**学术工坊新增文件（同步时不可覆盖）**：
  - `scripts/template_dissector.py` ⭐
  - `scripts/taste_guardian_cli.py` ⭐
  - `references/strategist.md` ⭐
  - `references/executor-base.md` ⭐
  - `references/executor-academic.md` ⭐
  - `references/taste_guardian.md` ⭐
  - `references/qa_defense.md` ⭐
  - `references/design-styles-excerpt.md` ⭐
  - `references/anti-slop-checklist.md` ⭐
  - `references/animation-restraint.md` ⭐
  - `references/editable-pptx-rules.md` ⭐
  - `references/gallery-showcase-excerpt.md` ⭐
  - `templates/layouts/zju_blue/` ⭐ (新写，不可覆盖)
  - `templates/design_spec_reference.md` ⭐ (学术扩展版，不可覆盖)
  - `workflows/dissect-template.md` ⭐
  - `docs/faq.md` ⭐
  - `docs/CHANGES.md` ⭐
  - `docs/regression-test-plan.md` ⭐
  - `SKILL.md` ⭐ (学术工坊专属，不可覆盖)

---

## scripts/ 目录

| 原始路径 | 学术工坊路径 | 文件数 | 修改 | 用途 |
|---------|-------------|--------|------|------|
| `scripts/*.py` (22个) | `scripts/*.py` | 22 | 0修改 | Step2项目管理/Step6质量检查/Step8导出 |
| `scripts/source_to_md/` | `scripts/source_to_md/` | 6 | 0修改 | Step1源内容转换 |
| `scripts/svg_to_pptx/` | `scripts/svg_to_pptx/` | 16 | 0修改 | Step8核心DrawingML转换器 |
| `scripts/svg_finalize/` | `scripts/svg_finalize/` | 7 | 0修改 | Step8.2 SVG后处理管线 |
| `scripts/svg_editor/` | `scripts/svg_editor/` | 6 | 0修改 | 可视化编辑workflow |
| `scripts/image_backends/` | `scripts/image_backends/` | 15 | 0修改 | AI图片生成(15后端含国产) |
| `scripts/image_sources/` | `scripts/image_sources/` | 5 | 0修改 | 图片搜索(4源) |
| `scripts/tts_backends/` | `scripts/tts_backends/` | 6 | 0修改 | TTS音频后端 |
| `scripts/template_import/` | `scripts/template_import/` | 3 | 0修改 | Step3模板解剖辅助 |
| `scripts/assets/` | `scripts/assets/` | 2 | 0修改 | 纹理资源 |
| `scripts/docs/` | `scripts/docs/` | 5 | 0修改 | 脚本文档 |

## templates/ 目录

| 原始路径 | 学术工坊路径 | 文件数 | 修改 | 用途 |
|---------|-------------|--------|------|------|
| `templates/layouts/` (21套) | `templates/layouts/` | 21目录 | 0修改 | Step4模板选择 |
| `templates/charts/` | `templates/charts/` | 73文件 | 0修改 | Step6图表页 |
| `templates/icons/` (5库) | `templates/icons/` | 5目录 | 0修改 | Step6图标嵌入(11631 SVG) |
| `templates/design_spec_reference.md` | `templates/design_spec_reference.md` | 1 | 扩展 | Step4八项确认(学术工坊扩展+2项) |
| `templates/spec_lock_reference.md` | `templates/spec_lock_reference.md` | 1 | 0修改 | Step4 spec锁模板 |

## references/ 目录

| 原始路径 | 学术工坊路径 | 文件数 | 修改 | 用途 |
|---------|-------------|--------|--------|------|
| `references/*.md` (14个) | `references/*.md` | 14 | 0修改 | Step4-6角色参考 |

## workflows/ 目录

| 原始路径 | 学术工坊路径 | 文件数 | 修改 | 用途 |
|---------|-------------|--------|--------|------|
| `workflows/*.md` (5个) | `workflows/*.md` | 5 | 0修改 | 5个独立workflow |

## 其他

| 原始路径 | 学术工坊路径 | 修改 | 用途 |
|---------|-------------|------|------|
| `requirements.txt` | `requirements.txt` | 0修改 | Python依赖 |

---

## 同步策略

### 手动同步流程（推荐）

当ppt-master上游更新时：
1. **检查上游版本**：
   ```bash
   # 在ppt-master仓库目录执行
   cd A:\claudeworks\ppt-master
   git log -1 --format="%H %ci"
   # 对比本表记录的拷贝日期 2026-05-04
   ```
2. **列出差异文件**：
   ```bash
   # 比较学术工坊和ppt-master的对应目录
   # 重点检查 scripts/ templates/layouts/ references/ workflows/
   diff -rq ~/.workbuddy/skills/ppt-master/scripts/ ~/.workbuddy/skills/academic-workshop/scripts/ --exclude="__pycache__" --exclude="template_dissector.py" --exclude="taste_guardian_cli.py"
   ```
3. **同步更新复用资产**（仅覆盖非⭐标记的文件）：
   ```bash
   # 示例：同步scripts顶层.py（不含新增2个⭐脚本）
   cp ~/.workbuddy/skills/ppt-master/scripts/*.py ~/.workbuddy/skills/academic-workshop/scripts/
   # 但需手动排除template_dissector.py和taste_guardian_cli.py不被覆盖
   ```
4. **更新本表的拷贝日期**：将新的日期写入`拷贝日期`字段
5. **验证**：运行svg_quality_checker.py确认脚本兼容性

### ⚠️ 不可覆盖清单（学术工坊新增文件）

以下文件是学术工坊新增的，**同步时绝对不能覆盖**：
- 标记⭐的17个文件/目录（见上方清单）
- 特别是 `SKILL.md`、`templates/layouts/zju_blue/`、`scripts/template_dissector.py`、`scripts/taste_guardian_cli.py`

### 自动同步脚本（可选）

可在学术工坊scripts目录创建 `sync_from_pptmaster.py`，自动对比两个目录的文件差异并生成同步报告（不含覆盖操作，仅列出差异）。

---

## 同步历史

| 日期 | 操作 | ppt-master版本 | 同步范围 | 备注 |
|------|------|---------------|---------|------|
| 2026-05-04 | 初始拷贝 | v2.5.0 | 全量（scripts+templates+references+workflows） | 学术工坊创建时一次性拷贝 |
| - | _待记录_ | - | - | - |
