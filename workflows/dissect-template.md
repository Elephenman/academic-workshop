# 模板解剖工作流 (Template Dissection Workflow)

> 独立工作流：当用户提供PPTX模板时，解剖模板提取设计基因，用于后续步骤继承。

---

## 触发条件

- 用户消息中包含`.pptx`文件路径（如"A:\kuake\浙大蓝.pptx"）
- 用户说"用XX模板"/"按照XX风格"（匹配`layouts_index.json`中的模板名）
- 用户说"解剖这个模板"/"分析这个PPT"

---

## 执行步骤

### 1. 检测模板来源

**情况A**：用户提供了PPTX文件路径 → 记录`template_path`，走解剖路线

**情况B**：用户说的是风格名 → 查`layouts_index.json`匹配：
```bash
cat ${SKILL_DIR}/templates/layouts/layouts_index.json
```
匹配到 → 复制对应模板目录的SVG和design_spec到项目目录，**跳过解剖**

**情况C**：都没有 → 自由设计路线，不触发本工作流

---

### 2. 运行模板解剖器

```bash
python3 ${SKILL_DIR}/scripts/template_dissector.py <pptx_path> <project_path>
```

解剖器执行流程：
1. 用python-pptx读取PPTX每页slide
2. 提取主题色（从theme XML解析clrScheme）
3. 提取主题字体（从theme XML解析fontScheme）
4. 逐页提取6类元素
5. 写入7个JSON文件到`template_elements/`
6. 自动生成`spec_lock.md` + `design_spec.md`

---

### 3. 解剖产出文件

| 文件 | 位置 | 内容 |
|------|------|------|
| `theme.json` | `template_elements/` | PPTX主题色+主题字体（从XML解析） |
| `color_palette.json` | `template_elements/` | 提取的色值+推荐主色/accent/background |
| `font_groups.json` | `template_elements/` | 字体名+使用次数+字号范围+推荐角色 |
| `layout_skeletons.json` | `template_elements/` | 每页shapes的position/size坐标系统 |
| `decorations.json` | `template_elements/` | 装饰元素（线条/角标/logo）+SVG片段+定位 |
| `placeholders.json` | `template_elements/` | 图文占位符（图片区域宽高比/文字框容量） |
| `rhythm_map.json` | `template_elements/` | 每页密度分类（anchor/dense/breathing） |
| `spec_lock.md` | 项目根目录 | 机器可读执行锁（色/字/图标/节奏） |
| `design_spec.md` | 项目根目录 | 人类可读设计叙事 |

---

### 4. 验证解剖结果

解剖完成后，AI检查以下关键指标：

| 检查项 | 通过标准 |
|--------|---------|
| 主题色数量 | ≥8个（dk1/lt1/accent1-6/hlink/folHlink） |
| 主色识别 | 权重最高的accent色被推荐为primary |
| 字体解析 | 主题字体已解析为实际字体名（非+mj-ea/+mn-ea占位符） |
| 节奏分布 | 同时有anchor+dense+breathing三种节奏 |
| spec_lock存在 | 非空文件 |
| design_spec存在 | 非空文件 |

---

### 5. 与Step 3衔接

解剖结果自动写入`spec_lock.md`和`design_spec.md`，后续Step 4八项确认将基于这些数据推荐色值/字体/节奏。

如果解剖结果不理想（如主题色提取不完整），AI可补充手动调整后再进入Step 4。

---

## 已知问题与注意事项

1. **GroupShape**：模板中包含组合形状时，解剖器会跳过其fill属性（GroupShape无fill）
2. **主题Part类型**：python-pptx对theme返回`Part`（非`XmlPart`），解剖器使用`etree.fromstring(blob)`解析
3. **schemeClr别名**：PPTX中bg1=lt1/tx1=dk1，解剖器已内置映射
4. **中文路径**：Python的pymupdf在含中文路径下可能import失败，需用`sys.path.insert`解决
5. **PowerShell输出**：Python输出在PowerShell中不可见，需写文件再读取
