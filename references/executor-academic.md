# 学术风格专属执行规则

> 新写：学术场景下的配色/字体/布局/图片规则

---

## 学术配色规则

### 底色

- 内容页：纯白 #FFFFFF 或暖白 #F8F8F6
- 封面：可使用主题色作背景（如浙大蓝#003366），但禁止渐变
- 禁止：纯黑底/深蓝底/渐变背景

### 主色使用

- 主色只用于：标题、强调文字、线条、装饰条
- 主色**不用于**：大面积背景、正文文字、图标填充
- 主色占比控制在10-20%（60-30-10法则：60%白+30%灰+10%主色）

### 灰色层级

```
近黑  #1D1D1F  — 主标题、重点文字
深灰  #545458  — 正文、副标题
中灰  #86868B  — 注释、来源标注
浅灰  #C7C7CC  — 分隔线、边框
极浅灰 #E5E5EA  — 卡片背景、次要分隔
```

---

## 学术字体规则

### 三字体栈

| 用途 | 英文 | 中文 | 备选 |
|------|------|------|------|
| Display | Source Serif 4 | 思源宋体 | Georgia / 宋体 |
| Body | -apple-system | Microsoft YaHei | PingFang SC |
| Mono | Consolas | - | SF Mono / JetBrains Mono |

### 字号层级

| 元素 | 字号(pt) | 字号(px) | 字重 |
|------|---------|---------|------|
| 封面标题 | 36-44 | 48-59 | 700 (Bold) |
| 页标题 | 28-32 | 37-43 | 600 (Semibold) |
| 副标题 | 20-24 | 27-32 | 400 (Regular) |
| 正文 | 18-22 | 24-29 | 400 (Regular) |
| 注释/引用 | 12-14 | 16-19 | 400 (Regular) |
| 代码 | 14-16 | 19-21 | 400 (Regular) |

> ⚠️ 正文字号绝对不低于18px（投影场景底线）

### 排版规则

- 行距：1.4-1.6倍字号
- 段间距：0.5-1倍字号
- 左对齐为主，居中仅用于封面/章节页/致谢页
- 右对齐：仅用于日期/页码

---

## 学术布局规则

### 封面（anchor节奏）

```
┌─────────────────────────────────────────────┐
│                                             │
│              （大面积留白≥40%）              │
│                                             │
│         论文标题（28-36pt，加粗）            │
│         The −10 region adjacent to ORFs...   │
│                                             │
│         作者 · 期刊 · 年份（16-18pt）        │
│         Zhong et al., LSA 2025              │
│                                             │
│              （大面积留白≥30%）              │
│                                             │
└─────────────────────────────────────────────┘
```

**SVG布局模板**（1280×720画布）：

```xml
<!-- 封面：标题居中偏上 + 作者信息区居下 + 大面积留白 -->
<!-- 顶部主题色横条 (h=100) -->
<rect x="0" y="0" width="1280" height="100" fill="[PRIMARY]"/>
<!-- 左侧accent竖条 -->
<rect x="0" y="0" width="6" height="100" fill="[ACCENT]"/>

<!-- 主标题区 (y=260-380) -->
<text x="640" y="320" text-anchor="middle" fill="[PRIMARY]" font-size="48-56" font-weight="bold">
  {{TITLE}}
</text>
<!-- 副标题/论文英文名 (y=380-420) -->
<text x="640" y="400" text-anchor="middle" fill="#545458" font-size="20-24">
  {{SUBTITLE}}
</text>

<!-- 分隔线 (y=440-460) -->
<line x1="440" y1="450" x2="840" y2="450" stroke="[SECONDARY]" stroke-width="2"/>
<circle cx="640" cy="450" r="5" fill="[ACCENT]"/>

<!-- 作者信息区 (y=480-600) -->
<text x="640" y="510" text-anchor="middle" fill="#1D1D1F" font-size="22-24">
  汇报人：{{AUTHOR}}
</text>
<text x="640" y="545" text-anchor="middle" fill="#545458" font-size="18-20">
  指导老师：{{ADVISOR}} | {{INSTITUTION}}
</text>
<text x="640" y="580" text-anchor="middle" fill="#86868B" font-size="16">
  {{DATE}}
</text>

<!-- 底部信息条 (y=665-720) -->
<rect x="0" y="665" width="1280" height="55" fill="#F5F7FA"/>
```

> 设计要点：标题上方留白≥160px，标题下方到作者区留白≥60px，整体留白率≥40%

---

### 方法流程（dense节奏）

**SVG布局模板 — 水平步骤条**：

```xml
<!-- 方法流程：3-5步水平步骤条 + 箭头连接 -->
<!-- 页眉区 -->
<rect x="0" y="0" width="1280" height="70" fill="[PRIMARY]"/>
<rect x="0" y="0" width="6" height="70" fill="[ACCENT]"/>
<text x="40" y="46" fill="#FFFFFF" font-size="28" font-weight="bold">
  方法流程
</text>

<!-- 步骤条区 (y=140-260) -->
<!-- 步骤1 -->
<rect x="60" y="150" width="220" height="80" rx="8" fill="#F5F7FA" stroke="[PRIMARY]" stroke-width="1.5"/>
<text x="170" y="185" text-anchor="middle" fill="[PRIMARY]" font-size="18" font-weight="bold">Step 1</text>
<text x="170" y="210" text-anchor="middle" fill="#1D1D1F" font-size="14">数据预处理</text>

<!-- 箭头1→2 -->
<line x1="280" y1="190" x2="330" y2="190" stroke="[SECONDARY]" stroke-width="2"/>
<polygon points="330,185 340,190 330,195" fill="[SECONDARY]"/>

<!-- 步骤2 -->
<rect x="340" y="150" width="220" height="80" rx="8" fill="#F5F7FA" stroke="[PRIMARY]" stroke-width="1.5"/>
<text x="450" y="185" text-anchor="middle" fill="[PRIMARY]" font-size="18" font-weight="bold">Step 2</text>
<text x="450" y="210" text-anchor="middle" fill="#1D1D1F" font-size="14">序列比对</text>

<!-- 箭头2→3 (继续...) -->

<!-- 详细说明区 (y=280-600) -->
<!-- 每步骤的展开说明，左对齐列表或小卡片 -->
```

**SVG布局模板 — 垂直流程图**（步骤较多时）：

```xml
<!-- 垂直流程：左侧时间线 + 右侧描述卡片 -->
<!-- 左侧时间线 -->
<line x1="120" y1="150" x2="120" y2="600" stroke="[PRIMARY]" stroke-width="2" stroke-opacity="0.3"/>
<!-- 时间点1 -->
<circle cx="120" cy="180" r="8" fill="[PRIMARY]"/>
<rect x="160" y="160" width="400" height="60" rx="6" fill="#F5F7FA"/>
<text x="180" y="185" fill="#1D1D1F" font-size="16" font-weight="bold">Step 1: Raw data collection</text>
<text x="180" y="205" fill="#545458" font-size="14">FASTQ files from NCBI SRA...</text>
<!-- 时间点2 (继续...) -->
```

> 设计要点：步骤≤5个，每步≤8字标题+1句展开。矩形浅灰填充+主色描边，箭头辅色。禁止3D/渐变/阴影。

---

### 关键结果（breathing节奏）⭐

**SVG布局模板 — 单大图+解读**：

```xml
<!-- 关键结果：大Figure占60-80%画布 + 一句解读 -->
<!-- 页眉区 -->
<rect x="0" y="0" width="1280" height="70" fill="[PRIMARY]"/>
<rect x="0" y="0" width="6" height="70" fill="[ACCENT]"/>
<text x="40" y="46" fill="#FFFFFF" font-size="28" font-weight="bold">
  关键结果
</text>

<!-- 大Figure (占画布60-80%) -->
<!-- 方案A: 图占左侧60%，解读占右侧40% -->
<image href="images/figure3a.png" 
       x="40" y="100" width="720" height="520" 
       preserveAspectRatio="xMidYMid meet"/>

<!-- 右侧解读区 -->
<text x="800" y="200" fill="[PRIMARY]" font-size="20" font-weight="bold">
  核心发现
</text>
<rect x="800" y="215" width="60" height="3" fill="[ACCENT]" rx="1"/>
<text x="800" y="260" fill="#1D1D1F" font-size="18">
  <tspan x="800" dy="0">该motif在Deinococcus-Thermus</tspan>
  <tspan x="800" dy="28">门中广泛分布于ORF邻近区域</tspan>
</text>
<!-- 来源标注 -->
<text x="40" y="650" fill="#86868B" font-size="12">
  来源: Fig. 3a, Zhong et al., LSA 2025
</text>
```

**方案B: 图占满宽，解读浮动在下方**：

```xml
<!-- 图占满宽 (y=100-480) -->
<image href="images/figure3a.png"
       x="40" y="100" width="1200" height="380"
       preserveAspectRatio="xMidYMid meet"/>

<!-- 解读浮动在Figure下方 -->
<text x="40" y="530" fill="#1D1D1F" font-size="20" font-weight="bold">
  核心发现：
</text>
<text x="40" y="560" fill="#1D1D1F" font-size="18">
  该motif在D.-T.门中广泛分布于ORF邻近区域，与翻译起始相关
</text>
<text x="40" y="590" fill="#86868B" font-size="14">
  来源: Fig. 3a, Zhong et al., LSA 2025
</text>
```

> 设计要点：Figure必须≥60%画布面积。一句解读≤30字。来源标注必须。**禁止多张小图堆叠**——每页只放1个核心Figure。次要结果放dense页。

---

### 讨论/局限（dense节奏）

**SVG布局模板 — 双列列表**：

```xml
<!-- 讨论/局限：2列对比或列表 -->
<!-- 页眉区 -->
<rect x="0" y="0" width="1280" height="70" fill="[PRIMARY]"/>
<rect x="0" y="0" width="6" height="70" fill="[ACCENT]"/>
<text x="40" y="46" fill="#FFFFFF" font-size="28" font-weight="bold">
  讨论
</text>

<!-- 核心观点条 -->
<rect x="0" y="70" width="1280" height="50" fill="#EBF2FA"/>
<rect x="0" y="70" width="6" height="50" fill="[SECONDARY]"/>
<text x="40" y="102" fill="#1D1D1F" font-size="18">
  {{KEY_MESSAGE}}
</text>

<!-- 左列：主要发现 (x=40-620) -->
<text x="40" y="160" fill="[PRIMARY]" font-size="22" font-weight="bold">主要发现</text>
<rect x="40" y="175" width="40" height="3" fill="[ACCENT]" rx="1"/>

<circle cx="55" cy="215" r="4" fill="[PRIMARY]"/>
<text x="70" y="220" fill="#1D1D1F" font-size="18">发现1描述...</text>
<circle cx="55" cy="255" r="4" fill="[PRIMARY]"/>
<text x="70" y="260" fill="#1D1D1F" font-size="18">发现2描述...</text>
<circle cx="55" cy="295" r="4" fill="[PRIMARY]"/>
<text x="70" y="300" fill="#1D1D1F" font-size="18">发现3描述...</text>

<!-- 右列：局限性 (x=660-1240) -->
<text x="660" y="160" fill="[PRIMARY]" font-size="22" font-weight="bold">局限性</text>
<rect x="660" y="175" width="40" height="3" fill="[ACCENT]" rx="1"/>

<circle cx="675" cy="215" r="4" fill="#86868B"/>
<text x="690" y="220" fill="#545458" font-size="18">局限1描述...</text>
<circle cx="675" cy="255" r="4" fill="#86868B"/>
<text x="690" y="260" fill="#545458" font-size="18">局限2描述...</text>
<circle cx="675" cy="295" r="4" fill="#86868B"/>
<text x="690" y="300" fill="#545458" font-size="18">局限3描述...</text>
```

**SVG布局模板 — 简洁表格**：

```xml
<!-- 对比表格 -->
<rect x="40" y="140" width="1200" height="40" fill="[PRIMARY]"/>
<text x="140" y="168" text-anchor="middle" fill="#FFFFFF" font-size="16" font-weight="bold">方法</text>
<text x="400" y="168" text-anchor="middle" fill="#FFFFFF" font-size="16" font-weight="bold">数据集</text>
<text x="660" y="168" text-anchor="middle" fill="#FFFFFF" font-size="16" font-weight="bold">准确率</text>
<text x="920" y="168" text-anchor="middle" fill="#FFFFFF" font-size="16" font-weight="bold">优势</text>

<!-- 数据行 (交替灰白背景) -->
<rect x="40" y="180" width="1200" height="40" fill="#FFFFFF"/>
<rect x="40" y="220" width="1200" height="40" fill="#F5F7FA"/>
<!-- ... -->
```

> 设计要点：每列≤5行文字，表头主色底白字，数据行交替灰白。局限/对比用中灰色区分态度。

---

### 总结展望（anchor节奏）

**SVG布局模板**：

```xml
<!-- 总结展望：1-3句核心结论 + 1句未来方向 + 大面积留白 -->
<!-- 页眉区 -->
<rect x="0" y="0" width="1280" height="70" fill="[PRIMARY]"/>
<rect x="0" y="0" width="6" height="70" fill="[ACCENT]"/>
<text x="40" y="46" fill="#FFFFFF" font-size="28" font-weight="bold">
  总结与展望
</text>

<!-- 核心结论区 (y=160-400, 左侧带accent竖条) -->
<rect x="60" y="160" width="4" height="60" fill="[ACCENT]" rx="2"/>
<text x="80" y="190" fill="#1D1D1F" font-size="22" font-weight="bold">
  核心结论
</text>

<!-- 结论1 (大字+简洁) -->
<text x="80" y="260" fill="#1D1D1F" font-size="24" font-weight="bold">
  1. 该motif在D.-T.门中广泛存在
</text>
<!-- 结论2 -->
<text x="80" y="310" fill="#1D1D1F" font-size="24" font-weight="bold">
  2. 位置偏好于ORF上游−10区域
</text>
<!-- 结论3 -->
<text x="80" y="360" fill="#1D1D1F" font-size="24" font-weight="bold">
  3. 可能参与翻译起始调控
</text>

<!-- 分隔线 -->
<line x1="80" y1="420" x2="1200" y2="420" stroke="#C7C7CC" stroke-width="1"/>

<!-- 未来方向 (y=440-520) -->
<text x="80" y="470" fill="[PRIMARY]" font-size="20" font-weight="bold">
  未来方向
</text>
<text x="80" y="510" fill="#545458" font-size="18">
  实验验证该motif的转录调控功能，扩展到其他嗜极微生物类群
</text>

<!-- 大面积留白 (y=520-665) -->
```

> 设计要点：结论用大字(24px+bold)，每句一行，不超过3句。未来方向用正文色(18px)。留白≥50%。**禁止**列表堆叠/信息过载。

---

## 学术图片规则

### 引用论文原图

```svg
<image href="images/figure3a.png" 
       x="100" y="80" width="480" height="360" 
       preserveAspectRatio="xMidYMid meet"/>
```

- 路径：`images/` 目录下的原图
- 保持原始宽高比：`preserveAspectRatio="xMidYMid meet"`
- 来源标注在图片下方

### SVG流程图

```svg
<rect x="100" y="200" width="160" height="50" rx="4" 
      fill="#F8F8F6" stroke="#003366" stroke-width="1.5"/>
<text x="180" y="230" text-anchor="middle" 
      font-family="Microsoft YaHei" font-size="14" fill="#1D1D1F">
  Step 1: 数据预处理
</text>
<line x1="260" y1="225" x2="320" y2="225" 
      stroke="#003366" stroke-width="1.5" marker-end="url(#arrowhead)"/>
```

- 矩形：浅灰填充+主色描边
- 箭头：主色，1.5px宽
- 文字：正文色，14-16px

### 禁止

- AI生成图片替代论文原图
- CSS剪影/SVG手画替代真实图
- 装饰性图片（与内容无内在关联）
