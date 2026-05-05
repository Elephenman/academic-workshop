# PPTX导出4条硬约束

> 来源：花叔Design `references/editable-pptx.md`
> 蒸馏日期：2026-05-04
> 蒸馏方式：提取4条核心约束，删除HTML-specific的详细实现说明
> 注意：学术工坊走SVG→DrawingML路线（ppt-master），不走HTML→PPTX路线（花叔Design）。
> 但这4条约束的精神适用于所有PPTX导出路径。

---

## 背景：为什么需要这4条约束

学术工坊使用ppt-master的SVG→DrawingML转换器（`scripts/svg_to_pptx/`），不是花叔Design的HTML→PPTX路径。但PowerPoint文件格式（OOXML）的物理约束是相同的：

- 文字必须在text frame里
- Shape和text frame是两个对象
- 渐变支持有限
- 图片必须引用真实文件

这4条约束是**OOXML格式本身的约束**投射到设计规范上的结果，不是工具链限制。

---

## 4条硬约束

### 规则1：文字必须包裹在文本容器中

SVG中：文字必须在`<text>`或`<tspan>`元素中，不能是裸路径文本。

PPTX中：文字必须在text frame（`<a:txBody>`）中，对应段落级元素。

**违反后果**：导出后文字无法编辑，或文字丢失。

### 规则2：不支持CSS渐变，只能用纯色

SVG中：避免`<linearGradient>`用于背景填充（装饰性渐变线条可以保留）。

PPTX中：shape fill只支持solid/gradient-fill两种，但转换器主要映射solid。

**违反后果**：渐变被替换为纯色或丢失。

### 规则3：背景/边框只能在容器元素上，不能在文字元素上

SVG中：`<rect>`承载背景/边框，`<text>`只负责文字渲染。

PPTX中：shape（方块）和text frame是两个对象，无法在同一element上同时画背景和写文字。

**违反后果**：文字元素的背景/边框丢失。

### 规则4：图片必须引用真实文件，不能用背景图片

SVG中：用`<image href="path/to/figure.png">`引用论文原图。

PPTX中：picture对象必须引用真实图片文件。

**违反后果**：背景图片方式引用的图片在PPTX中丢失。

---

## 学术场景特别提醒

1. **论文Figure必须用`<image>`引用原图**——不要用SVG手画替代，不要用AI生成替代
2. **封面标题用衬线字体**——Source Serif 4 / Georgia / 宋体
3. **正文字号≥18px**——投影场景最小可读字号
4. **代码块用等宽字体**——Consolas / SF Mono / 等线
5. **色值一致性**——所有页面只用spec_lock.md中定义的色值，不允许临场发明新颜色
