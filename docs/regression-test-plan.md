# 学术工坊全流程回归测试方案

> 版本：v0.1.0
> 日期：2026-05-04
> 状态：方案设计完成，待用户实际使用时验证

---

## 测试目标

验证学术工坊9步流水线在不同论文类型下的完整可运行性和产出质量。

## 测试矩阵（3种论文类型）

| # | 论文类型 | 特征 | 推荐论文 | 预期挑战 |
|---|---------|------|---------|---------|
| T1 | **生信方法论文** | 方法流程为主，Figure含流程图/热图/火山图 | Deinococcus-Thermus -10motif (Zhong et al., LSA 2025) | 流程图SVG绘制、热图引用 |
| T2 | **实验结果论文** | Figure为主（3-6张核心结果图），方法简短 | 任选一篇Cell/Nature子刊实验论文 | 大Figure嵌入、breathing页节奏 |
| T3 | **综述论文** | 文字为主（少Figure），大量引用 | 任选一篇Nature Reviews综述 | 文字密度高、需强制breathing页防均匀网格 |

## 每个测试的执行步骤

### 通用流程（适用于T1-T3）

1. **准备输入**：论文PDF路径（或已跑过的深读笔记）
2. **Step 1：输入接收**
   - PDF路线：`python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>`
   - 深读路线：直接读取深读笔记Markdown
   - 检查点：源内容文本完整、图片已提取
3. **Step 2：项目初始化**
   - `python3 ${SKILL_DIR}/scripts/project_manager.py init <name> --format ppt169`
   - `python3 ${SKILL_DIR}/scripts/project_manager.py import-sources <path> <source> --move`
   - `mkdir <path>/template_elements && mkdir <path>/notes`
   - 检查点：项目目录结构完整
4. **Step 3：模板解剖**（条件触发）
   - 自由设计路线：直接进入Step 4
   - 模板路线：提供PPTX → `python3 ${SKILL_DIR}/scripts/template_dissector.py <pptx> <path>`
   - 检查点：6个JSON产出、spec_lock.md写入、design_spec.md写入
5. **Step 4：八项确认 ⛔ BLOCKING**
   - 读取references/strategist.md + 设计参考
   - AI分析源内容，生成八项清单
   - 用户确认后 → 写入design_spec.md + spec_lock.md
   - 检查点：八项清单内容合理、用户已确认
6. **Step 5：品味守卫**
   - 读取references/taste_guardian.md
   - AI对照10条规则扫描design_spec.md
   - 可选：`python3 ${SKILL_DIR}/scripts/taste_guardian_cli.py <path>/design_spec.md`
   - 检查点：0个🔴禁止项、taste_report.md生成
7. **Step 6：逐页SVG生成**
   - 读取references/executor-base.md + executor-academic.md + shared-standards.md
   - 每页前重读spec_lock.md
   - 按节奏标签执行布局（anchor/dense/breathing）
   - 检查点：SVG文件数与页数一致、每页节奏标签匹配
8. **Step 7：逐字稿+Q&A防御**
   - 生成口语化逐字稿 → notes/total.md
   - 模拟导师视角生成Q&A → notes/qa_defense.md
   - 检查点：逐字稿覆盖所有页、Q&A每页3-5个追问
9. **Step 8：后处理+PPTX导出**
   - `python3 ${SKILL_DIR}/scripts/total_md_split.py <path>`
   - `python3 ${SKILL_DIR}/scripts/finalize_svg.py <path>`
   - `python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <path>`
   - 检查点：output/目录有PPTX文件、文件大小>10KB、可正常打开

### T1特有验证点（生信方法论文）

- 方法流程页：步骤条或流程图SVG正确渲染
- 结果页：热图/火山图原图引用路径正确
- 品味守卫：检测到"均匀卡片网格"风险（方法页容易堆叠卡片）→ 修复为breathing页

### T2特有验证点（实验结果论文）

- 关键结果页：大Figure占60%画布、一句解读浮动标题
- Figure嵌入：`images/`目录图片被正确引用
- 品味守卫：检测到"CSS剪影代替真实图"风险 → 强制使用原图

### T3特有验证点（综述论文）

- 文字密度页：强制插入breathing页（每3个dense页后1个breathing页）
- 品味守卫：检测到"信息密度过高"风险（dense页超4块） → 建议拆页
- 引用格式：引号引用而非emoji图标

## 自动化验证脚本（可编写）

```bash
# 验证PPTX产出完整性
python3 -c "
import os, sys
path = sys.argv[1]
# 检查output/目录有pptx文件
output_dir = os.path.join(path, 'output')
pptx_files = [f for f in os.listdir(output_dir) if f.endswith('.pptx')]
assert len(pptx_files) > 0, 'No PPTX file found'
# 检查文件大小
for f in pptx_files:
    size = os.path.getsize(os.path.join(output_dir, f))
    assert size > 10240, f'{f} too small ({size} bytes)'
# 检查逐字稿和Q&A
notes_dir = os.path.join(path, 'notes')
assert os.path.exists(os.path.join(notes_dir, 'total.md')), 'No script found'
assert os.path.exists(os.path.join(notes_dir, 'qa_defense.md')), 'No Q&A defense found'
# 检查品味报告
assert os.path.exists(os.path.join(path, 'taste_report.md')), 'No taste report found'
print('All checks PASSED')
" <project_path>
```

## 手动验证清单

| # | 检查项 | 方法 | 通过标准 |
|---|--------|------|---------|
| 1 | PPTX可打开 | PowerPoint/WPS打开 | 无损坏、页数正确 |
| 2 | 品味视觉 | 人眼看PPT | 无紫渐变/Emoji/均匀网格 |
| 3 | 逐字稿口语化 | 读逐字稿 | 无书面过渡词、句长适合口语 |
| 4 | Q&A防御针对性 | 读Q&A | 围绕"对本组的用处"、不卑不亢 |
| 5 | Figure引用 | 检查结果页 | 原图显示、非AI生成替代 |

## 测试优先级

- **P0（必须通过）**：T1（已有Deinococcus论文测试经验）
- **P1（应该通过）**：T2（实验结果论文，验证Figure嵌入路线）
- **P2（可选通过）**：T3（综述论文，验证文字密度路线）

## 实施建议

> 由于测试需要实际论文输入，建议在用户首次使用学术工坊时自然验证。
> 每次完整使用后，将产出结果记录到此文档的"测试结果"章节。

---

## 测试结果（待填写）

| # | 论文 | 日期 | 结果 | 问题 |
|---|------|------|------|------|
| T1 | _待用户使用时填写_ | - | - | - |
| T2 | _待用户使用时填写_ | - | - | - |
| T3 | _待用户使用时填写_ | - | - | - |