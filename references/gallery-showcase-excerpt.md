# 结果页展示风格参考（学术版）

> 来源：花叔Design `references/apple-gallery-showcase.md`
> 蒸馏日期：2026-05-04
> 蒸馏方式：提取结果页"大图+解读"的视觉Token，删除3D倾斜/动画/画廊模式
> 学术适配：组会PPT的结果页是视觉高潮，不是信息堆叠

---

## 核心原则：结果页是视觉冲击页

组会PPT的"关键结果"页应该标记为`breathing`节奏，不是`dense`。

**为什么？**
- 结果页是观众最关心的部分——你的核心发现在这里
- 一张大Figure + 一句解读，比6张小图堆叠有说服力10倍
- 视觉冲击 > 信息密度——让观众"看到"结果，不是"读完"结果

---

## 结果页视觉Token

### 色板（学术版）

```css
:root {
  --bg:         #FFFFFF;    /* 主画布底 — 学术白 */
  --bg-warm:    #F8F8F6;    /* 温暖米白 */
  --ink:        #1D1D1F;    /* 主字色 */
  --ink-60:     #545458;    /* 次级文字 */
  --muted:      #86868B;    /* 注释文字 */
  --hairline:   #E5E5EA;    /* 分隔线 */
  --accent:     #003366;    /* 学术蓝 — 默认浙大蓝 */
  --accent-deep:#001A33;    /* 深学术蓝 */
}
```

### 字体栈

```css
:root {
  --serif-cn:  "Source Han Serif SC", "Songti SC", "SimSun", Georgia, serif;
  --serif-en:  "Source Serif 4", Georgia, serif;
  --sans:      "Microsoft YaHei", -apple-system, "PingFang SC", system-ui;
  --mono:      "Consolas", "SF Mono", "JetBrains Mono", ui-monospace;
}
```

---

## 结果页3种布局模式

### 模式A：全幅大图 + 浮动标题

```
┌────────────────────────────────────────────┐
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │                                      │  │
│  │          论文Figure                  │  │
│  │          占80%画布                    │  │
│  │                                      │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  Figure 3: 一句解读文字                     │
│  来源: Author et al., 2025                 │
└────────────────────────────────────────────┘
```

- Figure用`<image>`引用论文原图
- 解读文字在底部，字号≥16px，颜色muted灰
- 来源标注在解读下方，字号12px

### 模式B：左图右解读

```
┌────────────────────────────────────────────┐
│                                            │
│  ┌─────────────────┐  关键发现             │
│  │                 │  ─────────            │
│  │   论文Figure    │  一句核心解读          │
│  │   占60%画布     │                        │
│  │                 │  数据要点1             │
│  │                 │  数据要点2             │
│  └─────────────────┘                        │
│                                            │
└────────────────────────────────────────────┘
```

- Figure占左侧60%
- 右侧：标题（accent色）+ 核心解读（1句）+ 数据要点（≤3条）
- 要点用小圆点标记，不用emoji

### 模式C：多Figure对比（仅限必须对比时）

```
┌────────────────────────────────────────────┐
│                                            │
│  ┌────────────┐     ┌────────────┐         │
│  │ Figure 3A  │     │ Figure 3B  │         │
│  │ 对照组     │     │ 实验组     │         │
│  └────────────┘     └────────────┘         │
│                                            │
│  A vs B: 一句对比解读                       │
└────────────────────────────────────────────┘
```

- 只在需要对比时用，不超过2张图
- 每张图下方标注(A)(B)
- 底部一句对比解读

---

## 质感细节

### 1. 图片边框

论文Figure加极淡边框（`stroke: #E5E5EA; stroke-width: 1`），不带边框也可以——取决于原图是否需要视觉框定。

### 2. 图注排版

```svg
<text y="offset" font-family="var(--sans)" font-size="12" fill="var(--muted)">
  Figure 3: The −10 region motif in Deinococcus-Thermus
</text>
<text y="offset+16" font-family="var(--mono)" font-size="10" fill="var(--muted)" opacity="0.7">
  Source: Zhong et al., Life Science Alliance 2025
</text>
```

### 3. 解读文字

解读文字是结果页最重要的文字——它告诉观众**看什么**和**为什么重要**。

- 字号≥18px（投影可读）
- 颜色用ink色（#1D1D1F），不是muted灰
- 最多1-2句，不要写段落
- 用断言句，不是描述句："Motif enrichment is 4.2-fold higher in promoter regions" > "The motif enrichment results show that..."

---

## 反面教材

| 反面做法 | 为什么不好 |
|---------|-----------|
| 6张小图堆满一页 | 每张图都看不清，信息过载 |
| Figure+3段解读文字 | 结果页不是文献综述 |
| 用AI生成图替代论文原图 | 学术诚信问题+信息失真 |
| 每张图都加icon标记 | 装饰性icon是slop |
| 彩色边框包围Figure | 分散注意力，图片本身足够 |
