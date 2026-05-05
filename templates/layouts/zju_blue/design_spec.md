# ZJU Blue Template - Design Specification

> Suitable for Zhejiang University academic group meetings, literature presentations, seminar reports, and research progress presentations.
> Based on: 文献汇报01-浙大蓝-多篇版.pptx (24-page template dissected via template_dissector.py)

---

## I. Template Overview

| Property       | Description                                            |
| -------------- | ------------------------------------------------------ |
| **Template Name** | zju_blue                                           |
| **Use Cases**  | ZJU academic group meetings, literature reviews, seminar presentations, research progress reports |
| **Design Tone** | Professional, clean, ZJU-branded, academic rigor     |
| **Theme Mode** | Light theme (white background + ZJU blue header)      |
| **Source Template** | 文献汇报01-浙大蓝-多篇版.pptx                     |

---

## II. Canvas Specification

| Property       | Value                         |
| -------------- | ----------------------------- |
| **Format**     | Standard 16:9                 |
| **Dimensions** | 1280 × 720 px                |
| **viewBox**    | `0 0 1280 720`                |
| **Page Margins** | Left/Right 40px, Top 0px, Bottom 35px |
| **Safe Area**  | x: 40-1240, y: 70-665        |

---

## III. Color Scheme

### Primary Colors (from template dissection)

| Role           | Value       | Notes                            |
| -------------- | ----------- | -------------------------------- |
| **ZJU Blue (Primary)** | `#003F88` | Header background, section titles, main decorations, theme accent1 |
| **ZJU Blue Secondary** | `#2B6CB0` | Card borders, icons, secondary decorations, flow arrows |
| **Accent Orange** | `#ED7D31` | Key highlights, left decorative bar, accent dots, theme accent2 |
| **Light Blue Tint** | `#EBF2FA` | Key message bar background, card inner sections |
| **Background White** | `#FFFFFF` | Page main background, theme lt1  |

### Text Colors (from template dissection)

| Role           | Value       | Usage                  |
| -------------- | ----------- | ---------------------- |
| **White Text** | `#FFFFFF`   | Text on dark backgrounds |
| **Primary Text** | `#1D1D1F` | Body content, theme dk1-variant |
| **Secondary Text** | `#545458` | Descriptions, annotations |
| **Muted Gray** | `#999999`  | Footer, auxiliary info |

### Neutral Colors

| Role           | Value       | Usage                  |
| -------------- | ----------- | ---------------------- |
| **Card Gray**  | `#F5F7FA`   | Card inner background, info blocks |
| **Border Gray** | `#D0D7E0`  | Card borders, dividers |

### Theme Color Reference (from PPTX theme)

| Scheme Name | HEX |
|-------------|-----|
| dk1 | `#000000` |
| lt1 | `#FFFFFF` |
| dk2 | `#44546A` |
| lt2 | `#E7E6E6` |
| accent1 | `#003F88` |
| accent2 | `#ED7D31` |
| accent3 | `#A5A5A5` |
| accent4 | `#FFC000` |
| accent5 | `#5B9BD5` |
| accent6 | `#70AD47` |
| hlink | `#0563C1` |
| folHlink | `#954F72` |
| _theme_name | `浙大蓝` |

---

## IV. Typography System

### Font Stack (from template dissection)

**Heading Font**: `"Source Han Sans CN", "思源黑体 CN", "Microsoft YaHei", Arial, sans-serif`
**Body Font**: `"Source Han Sans CN Light", "思源黑体 CN Light", "Microsoft YaHei", Arial, sans-serif`

> Source: PPTX theme +mj-ea = 思源黑体 CN, +mn-ea = 思源黑体 CN Light

### Font Size Hierarchy

| Level | Usage            | Size | Weight  | Font             |
| ----- | ---------------- | ---- | ------- | ---------------- |
| H1    | Cover main title | 56px | Bold    | Source Han Sans CN |
| H2    | Page title       | 28px | Bold    | Source Han Sans CN |
| H3    | Chapter title    | 56px | Bold    | Source Han Sans CN |
| H4    | Card title       | 22px | Bold    | Source Han Sans CN |
| P     | Body content     | 18px | Regular | Source Han Sans CN Light |
| High  | Highlighted data | 36px | Bold    | Source Han Sans CN |
| Sub   | Notes/sources    | 14px | Regular | Source Han Sans CN Light |
| XS    | Page number/copyright | 12px | Regular | Source Han Sans CN Light |

---

## V. Page Structure

### General Layout

| Area           | Position/Height | Description                            |
| -------------- | --------------- | -------------------------------------- |
| **Header**     | y=0, h=70px     | ZJU blue background + orange left bar + page title |
| **Key Message Bar** | y=70, h=50px | Core message/summary area (light blue tint background) |
| **Content Area** | y=135, h=515px | Main content area                    |
| **Footer**     | y=665, h=55px   | Data source, section name, page number |

### Decorative Elements

- **Left Orange Bar**: Orange (`#ED7D31`), width 6px, used for header and card decoration
- **Blue Border**: ZJU blue secondary (`#2B6CB0`), used for card borders and flow arrows
- **Accent Dot**: Orange (`#ED7D31`), used at divider line center

---

## VI. Page Types

### 1. Cover Page (01_cover.svg)

- White background
- ZJU blue top bar + orange left vertical bar decoration
- Top-right Logo placeholder area
- Centered main title + subtitle
- Decorative divider line (blue + orange center dot)
- Presenter info area (name, advisor, institution)
- Bottom gray info area (date)

### 2. Table of Contents Page (02_toc.svg)

- White background
- Standard header (ZJU blue + orange vertical bar)
- Card-style TOC item layout (2 columns)
- Light gray background cards + left colored vertical bar (alternating orange/blue)
- Each card: title (bold blue) + description (light gray text)

### 3. Chapter Divider Page (02_chapter.svg)

- ZJU blue full-screen background (`#003F88`)
- Right-side geometric line decorations (subtle)
- Left orange vertical bar decoration
- Large semi-transparent background number
- Prominent white chapter title
- Light blue chapter description
- Orange decorative horizontal line

### 4. Content Page (03_content.svg)

- White background
- Standard header (ZJU blue + orange vertical bar)
- Key message bar (light blue tint background + blue left vertical bar)
- Flexible content area
- Footer: data source, section name, page number

### 5. Ending Page (04_ending.svg)

- White background
- ZJU blue top bar
- Centered thank-you message
- Tagline/subtitle
- Decorative divider line (blue + orange center dot)
- Contact info card (gray background)
- Bottom gray area (copyright, page number)

---

## VII. Layout Patterns

| Pattern            | Use Cases                      |
| ------------------ | ------------------------------ |
| **Single Column Centered** | Cover, ending, key points |
| **Two-Column Cards** | Table of contents            |
| **Left-Right Split (5:5)** | Comparison display      |
| **Left-Right Split (4:6)** | Image-text mixed layout |
| **Card Grid**      | Research content list           |
| **Timeline**       | Research progress               |
| **Big Figure + Insight** | Results pages (breathing) |

---

## VIII. Rhythm Guidelines (from template dissection)

> The source template has 24 pages with a healthy rhythm:
> - 2 anchor pages (cover P01 + ending P24)
> - 12 dense pages (information-heavy)
> - 10 breathing pages (low density, visual impact)

**Recommended rhythm for group meeting presentations:**

| Page Type | Rhythm | Density | Design Rule |
|-----------|--------|---------|-------------|
| Cover | anchor | <0.3 | Title + author + institution, 60%+ whitespace |
| Background | dense | 0.3-0.5 | Text-focused, max 3 key points |
| Method | dense | 0.4-0.6 | Flow chart or step list |
| Key Result | breathing | <0.3 | Big Figure (60% canvas) + one insight |
| Discussion | dense | 0.3-0.5 | List or concise table |
| Summary | anchor | <0.3 | 1-3 core conclusions + future direction, 60%+ whitespace |
| Thanks | anchor | <0.1 | Simple, minimal decoration |

---

## IX. SVG Technical Constraints

### Mandatory Rules

1. viewBox: `0 0 1280 720`
2. Use `<rect>` elements for backgrounds
3. Use `<tspan>` for text wrapping (no `<foreignObject>`)
4. Use `fill-opacity` / `stroke-opacity` for transparency; no `rgba()`
5. Prohibited: `mask`, `<style>`, `class`, `foreignObject`. `clipPath` is allowed only on `<image>` under `shared-standards.md` §1.2
6. Prohibited: `textPath`, `animate*`, `script`
7. `marker-start` / `marker-end` conditionally allowed (marker in `<defs>`, `orient="auto"`, shape = triangle/diamond/oval) — see shared-standards.md §1.1

### PPT Compatibility Rules

- No `<g opacity="...">` (group opacity); set opacity on each child element individually
- Use overlay layers for image transparency
- Inline styles only; no external CSS or `@font-face`

---

## X. Placeholder Specification

Templates use `{{PLACEHOLDER}}` format placeholders. Common placeholders:

| Placeholder        | Description        |
| ------------------ | ------------------ |
| `{{TITLE}}`        | Paper/project main title |
| `{{SUBTITLE}}`     | Subtitle           |
| `{{AUTHOR}}`       | Presenter name     |
| `{{ADVISOR}}`      | Advisor            |
| `{{INSTITUTION}}`  | University/institution |
| `{{DATE}}`         | Presentation date  |
| `{{PAGE_TITLE}}`   | Page title         |
| `{{SECTION_NUM}}`  | Section number     |
| `{{CHAPTER_NUM}}`  | Chapter number (large) |
| `{{CHAPTER_TITLE}}`| Chapter title      |
| `{{CHAPTER_DESC}}` | Chapter description |
| `{{KEY_MESSAGE}}`  | Key message        |
| `{{PAGE_NUM}}`     | Page number        |
| `{{SOURCE}}`       | Data source        |
| `{{SECTION_NAME}}` | Section name (footer) |
| `{{TOC_ITEM_N_TITLE}}` | TOC item title (N=1..n) |
| `{{TOC_ITEM_N_DESC}}` | TOC item description (N=1..n) |
| `{{THANK_YOU}}`    | Thank-you message  |
| `{{ENDING_SUBTITLE}}` | Ending subtitle/tagline |
| `{{CONTACT_INFO}}` | Contact information |
| `{{EMAIL}}`        | Email address      |
| `{{COPYRIGHT}}`    | Copyright info     |
| `{{LOGO}}`         | Logo text (ZJU emblem) |
| `{{CONTENT_AREA}}` | Flexible content area placeholder |

---

## XI. Component Specifications

### 1. Tag

```xml
<!-- ZJU Blue background white text tag -->
<rect x="40" y="150" width="80" height="28" fill="#2B6CB0" rx="4"/>
<text x="80" y="170" text-anchor="middle" fill="#FFFFFF" font-size="14" font-weight="bold">内容详解</text>

<!-- Orange background white text tag (emphasis) -->
<rect x="40" y="150" width="80" height="28" fill="#ED7D31" rx="4"/>
<text x="80" y="170" text-anchor="middle" fill="#FFFFFF" font-size="14" font-weight="bold">核心发现</text>
```

### 2. Flow Arrow

```xml
<!-- Horizontal flow arrow -->
<line x1="200" y1="300" x2="350" y2="300" stroke="#2B6CB0" stroke-width="2"/>
<polygon points="350,295 360,300 350,305" fill="#2B6CB0"/>
```

### 3. Data Highlight Box

```xml
<!-- Key data block -->
<rect x="40" y="400" width="200" height="80" fill="#FFFFFF" stroke="#ED7D31" stroke-width="2" rx="8"/>
<text x="140" y="445" text-anchor="middle" fill="#ED7D31" font-size="24" font-weight="bold">30%</text>
<text x="140" y="470" text-anchor="middle" fill="#545458" font-size="12">关键指标</text>
```

---

## XII. Usage Instructions

1. Select this template when the user says "浙大蓝" or "ZJU Blue" or is a Zhejiang University student
2. Cover page: fill in paper title, author info, and date
3. Content pages: use header + key message bar + flexible content area
4. Result pages: use breathing rhythm with big figure + one insight
5. Chapter dividers: use full-screen ZJU blue background for section transitions
6. Ensure all placeholder content is replaced before final SVG generation
7. Font stack: Source Han Sans CN for headings, Source Han Sans CN Light for body text
