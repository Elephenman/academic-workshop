# -*- coding: utf-8 -*-
"""md_to_svg.py — 通用 Markdown → 学术组会 PPT (SVG) 生成器。

把任意论文 / 文献 Markdown 直接变成一套符合 `references/md_driven_content.md`
准则的浙大蓝 16:9 SVG 页面，再用 `svg_to_pptx.py` 导出可编辑 PPTX 即可。

设计原则（与 skill 优化一致）：
  * 镜像 md 逻辑分区：封面 → Agenda → 每 ## 一节（章节分隔页 + 内容页）。
  * 图按 md 内位置落位，原宽高比（preserveAspectRatio="xMidYMid meet"），不裁切。
  * 正文用大字号（正文 13.5–15pt），每个逻辑段落 = 一个文本框（data-wrap-w 段落级），
    段内多行用无定位 <tspan> 折叠进同一框。

用法：
    python md_to_svg.py INPUT.md [--out DIR] [--title "..."] [--authors "..."]
    python md_to_svg.py INPUT.md --curation deck.json   # 编排驱动，达到旧版叙事效果

输出 DIR/ 下：svg_output/*.svg（每页一文件）、images/*.png（拷贝+必要时降采样）、notes/*.md（演讲备注）。
无 --curation 时按 md 标题机械切片（已做去套话/跨页去重）；带 --curation 时按编排数据
（章节分隔 / 结果四段式 / 版式分化）渲染，复刻手工编排质感。
"""
import os
import re
import math
import shutil
import argparse

# ---------------- 画布与版式 ----------------
W, H = 1280, 720
ML, MR = 40, 40
CW = W - ML - MR            # 1200
HDR_H = 70                  # 蓝色页眉带
KEY_H = 54                  # key-message 条
CTOP = HDR_H + KEY_H + 12   # 内容区顶
CONTENT_BOT = 640
CH = CONTENT_BOT - CTOP     # ~504
FIG_H = 430                 # 结果图高度（图高优先，宽按源比例）

# ---------------- 字号体系（px；1px = 0.75pt）----------------
FS_TITLE   = 30
FS_KEY     = 18
FS_BODY    = 18   # 一般段落（~13.5pt）
FS_BODY2   = 20   # 结果页段落（~15pt，最显眼）
FS_TAG     = 15
FS_CARD_H  = 18
FS_BULLET  = 19
FS_SMALL   = 13
FS_COVER_T = 42
FS_COVER_S = 26
FS_COVER_D = 18

FONT_CN = "'Microsoft YaHei','微软雅黑',sans-serif"
FONT_EN = "'Georgia','Times New Roman',serif"

# ---------------- 浙大蓝 palette ----------------
BLUE   = "#003F88"
BLUE2  = "#2B6CB0"
ORANGE = "#ED7D31"
PALE   = "#EBF2FA"
LINE   = "#D0D7E0"
LINE2  = "#C2D2E8"
INK    = "#1D1D1F"
GRAY   = "#545458"
LGRAY  = "#999999"

TOTAL = 1   # 总页数占位，main 里在生成前算准


# ---------------- 文本工具 ----------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clean_md(s):
    """去除 Markdown / Obsidian 标记，避免泄漏进 PPT：
    **粗体** *斜体* __ ** `代码`，以及引用块 '>' 与 Obsidian callout '[!type]-'。
    """
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"\1", s)
    s = re.sub(r"__(.+?)__", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    # 引用块 / Obsidian callout 标记：'> [!tip]- 标题' -> '标题'
    s = re.sub(r"^[>\s]+", "", s)            # 行首 > 与空白
    s = re.sub(r"^\[\!\w+\][-]?\s*", "", s)  # [!note]- / [!tip] 等
    return s.strip()


def char_w(c, fs):
    o = ord(c)
    if o >= 0x2E80 or 0xFF00 <= o <= 0xFFEF:
        return fs * 1.0
    if c == " ":
        return fs * 0.35
    if c.isascii():
        return fs * 0.55 if c.isalnum() else fs * 0.5
    return fs * 0.6


def tokenize(text):
    toks = []
    buf = ""

    def flush():
        nonlocal buf
        if buf:
            toks.append(("w", buf))
            buf = ""

    for ch in text:
        if ch.isspace():
            flush()
            toks.append(("s", ch))
        elif ord(ch) >= 0x2E80 or 0xFF00 <= ord(ch) <= 0xFFEF:
            flush()
            toks.append(("c", ch))
        elif ch.isalnum() or ch in "+-/.,()%*²⁺×≈αβ<>–—":
            buf += ch
        else:
            flush()
            toks.append(("c", ch))
    flush()
    return toks


def wrap_text(text, max_w, fs):
    toks = tokenize(text)
    lines = []
    line = ""

    def width(s):
        return sum(char_w(c, fs) for c in s)

    for typ, val in toks:
        if typ == "s":
            if line == "":
                continue
            cand = line + val
            if width(cand) <= max_w:
                line = cand
            else:
                lines.append(line)
                line = ""
        else:
            cand = line + val
            if width(cand) <= max_w or width(line) == 0:
                line = cand
            else:
                lines.append(line)
                line = val
    if line:
        lines.append(line)
    return lines


def est_lines(text, fs, max_w):
    """估计换行后的可视行数——必须与转换器 _estimate_wrapped_lines 一致
    （cjk*fs + other*fs*0.5），否则生成器堆叠文本框会重叠。"""
    if max_w <= 0:
        return 1
    total = 0
    for line in text.split("\n"):
        if not line.strip():
            total += 1
            continue
        cjk = sum(1 for c in line if ord(c) >= 0x2E80 or 0xFF00 <= ord(c) <= 0xFFEF)
        other = len(line) - cjk
        w = cjk * fs + other * fs * 0.5
        total += max(1, math.ceil(w / max_w))
    return max(1, total)


def _box_h(lines_n, fs):
    pad = fs * 0.15
    return lines_n * fs * 1.5 + pad * 2 + fs * 0.3


def para_box(text, x, y, w, fs, out, fill=INK, weight="400", gap=4):
    """一个逻辑段落 = 一个自动换行文本框（data-wrap-w）。返回下一元素 y。"""
    s = (f'<text x="{x}" y="{y+fs*0.82}" data-wrap-w="{w}" font-family="{FONT_CN}" '
         f'font-size="{fs}" font-weight="{weight}" fill="{fill}" text-anchor="start">'
         f'{esc(text)}</text>')
    out.append(s)
    return y + _box_h(est_lines(text, fs, w), fs) + gap


def para_box_multi(lines_list, x, y, w, fs, out, fill=INK, weight="400", gap=4):
    """一个框内多行：每行是子 <tspan>（无 x/y/dy），转换器保留为同一框 + <a:br/>。"""
    if not lines_list:
        return y
    first = esc(lines_list[0])
    rest = "".join(f"<tspan>{esc(t)}</tspan>" for t in lines_list[1:])
    s = (f'<text x="{x}" y="{y+fs*0.82}" data-wrap-w="{w}" font-family="{FONT_CN}" '
         f'font-size="{fs}" font-weight="{weight}" fill="{fill}" text-anchor="start">'
         f'{first}{rest}</text>')
    out.append(s)
    total = sum(est_lines(t, fs, w) for t in lines_list)
    return y + _box_h(total, fs) + gap


def T(x, y, s, fs, font=FONT_CN, fill=INK, weight="400", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{fs}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')


def bullets(items, x, y, max_w, fs, out, gap=16):
    for it in items:
        y = para_box("• " + it, x + 18, y, max_w - 18, fs, out, INK, "400", gap)
    return y


def figure(href, x, y, w, h, out):
    out.append(f'<rect x="{x+5}" y="{y+5}" width="{w}" height="{h}" fill="{PALE}" rx="2"/>')
    out.append(f'<image href="{href}" x="{x}" y="{y}" width="{w}" height="{h}" '
               f'preserveAspectRatio="xMidYMid meet"/>')
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
               f'stroke="{BLUE}" stroke-width="1.5" rx="2"/>')


def tag(out, text, x, y, fill=BLUE):
    w = len(text) * FS_TAG + 20
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="4" fill="{fill}"/>')
    out.append(T(x + 10, y + 16, text, FS_TAG, FONT_CN, "#FFFFFF", "700"))
    return y + 32


def header_band(out, sec_num, title, key_msg=""):
    out.append(f'<rect x="0" y="0" width="{W}" height="{HDR_H}" fill="{BLUE}"/>')
    out.append(f'<rect x="0" y="0" width="6" height="{HDR_H}" fill="{ORANGE}"/>')
    txt = (f"{sec_num}  " if sec_num else "") + title
    out.append(T(ML + 10, 47, txt, FS_TITLE, FONT_CN, "#FFFFFF", "700"))
    out.append(T(W - 40, 47, "浙江大学", 15, FONT_CN, "#FFFFFF", "400", "end"))
    if key_msg:
        out.append(f'<rect x="0" y="{HDR_H}" width="{W}" height="{KEY_H}" fill="{PALE}"/>')
        out.append(f'<rect x="0" y="{HDR_H}" width="6" height="{KEY_H}" fill="{BLUE2}"/>')
        para_box(key_msg, ML + 10, HDR_H, CW - 40, FS_KEY, out, INK, "600", gap=0)


def footer(n, section_name=""):
    parts = [f'<line x1="{ML}" y1="662" x2="{W-MR}" y2="662" stroke="{PALE}" stroke-width="1"/>']
    if section_name:
        parts.append(T(640, 690, section_name, FS_SMALL, FONT_CN, LGRAY, "400", "middle"))
    parts.append(T(W - MR, 690, f"{n} / {TOTAL}", FS_SMALL, FONT_CN, GRAY, "600", "end"))
    return "\n".join(parts)


def svg_open():
    return [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>']


def svg_close(n, section_name=""):
    return [footer(n, section_name), "</svg>"]


def content_slide(sec_num, title, key_msg, body, n, section_name):
    out = svg_open()
    header_band(out, sec_num, title, key_msg)
    out.extend(body)
    out.extend(svg_close(n, section_name))
    return "\n".join(out)


def draw_box(x, y, w, h, label, fs, out, fill=PALE, stroke=BLUE):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" '
               f'stroke="{stroke}" stroke-width="1.5"/>')
    lines = []
    for part in label.split("\n"):
        lines += wrap_text(part, w - 22, fs)
    lh = fs * 1.3
    total = len(lines) * lh
    start = y + (h - total) / 2 + fs * 0.82
    for i, ln in enumerate(lines):
        out.append(T(x + w / 2, start + i * lh, ln, fs, FONT_CN, INK, "400", "middle"))


def arrow(x1, y1, x2, y2, out, color=BLUE):
    out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5"/>')
    ang = math.atan2(y2 - y1, x2 - x1)
    sz = 7
    a1 = ang + math.radians(150)
    a2 = ang - math.radians(150)
    p1 = (x2 + sz * math.cos(a1), y2 + sz * math.sin(a1))
    p2 = (x2 + sz * math.cos(a2), y2 + sz * math.sin(a2))
    out.append(f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


# ---------------- Markdown 解析 ----------------
IMG_OBSIDIAN = re.compile(r"!\[\[([^\]]+)\]\]")
IMG_MD = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")
SEP_RE = re.compile(r"^\s*\|?[\s:\-|]+\|?\s*$")


def _clean_cell(s):
    # 表格单元格同样需要去除 Markdown 强调标记（**粗体**/*斜体*/`代码`），
    # 否则会泄漏进 PPT 文本（如 **模板酶结构**）。
    return clean_md(s.strip().strip("|").strip())


def parse_md(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    doc = {"title": None, "authors": "", "sections": [], "lead": []}
    # YAML frontmatter (--- ... ---) 跳过，避免泄漏进封面摘要；
    # 同时抽取 authors / title 用于封面。
    start = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                for k in range(1, j):
                    kv = lines[k].split(":", 1)
                    if len(kv) == 2:
                        key = kv[0].strip()
                        val = kv[1].strip().strip('"').strip("'")
                        if key == "authors":
                            doc["authors"] = val
                        elif key == "title" and not doc["title"]:
                            doc["title"] = clean_md(val)
                start = j + 1
                break
        lines = lines[start:]
    cur = None
    sub = None
    in_table = False
    table_buf = []

    def flush_table():
        nonlocal in_table, table_buf
        if in_table and table_buf:
            # 去掉分隔行
            rows = [r for r in table_buf if not SEP_RE.match(r)]
            # 第一行当表头
            if rows:
                header = [_clean_cell(c) for c in rows[0].split("|")]
                data = [[_clean_cell(c) for c in r.split("|")] for r in rows[1:]]
                target = sub if sub else cur
                if target is not None:
                    target["tables"].append((header, data))
        in_table = False
        table_buf = []

    for raw in lines:
        line = raw.rstrip("\n")
        if line.startswith("# "):
            flush_table()
            doc["title"] = clean_md(line[2:])
            cur = None
            sub = None
            continue
        if line.startswith("## "):
            flush_table()
            cur = {"heading": clean_md(line[3:]), "paras": [], "images": [],
                   "subs": [], "tables": [], "bullets": []}
            doc["sections"].append(cur)
            sub = None
            continue
        if line.startswith("### "):
            flush_table()
            if cur is not None:
                sub = {"heading": clean_md(line[4:]), "paras": [], "images": [], "bullets": [], "tables": []}
                cur["subs"].append(sub)
            continue
        # 表格
        if TABLE_RE.match(line):
            in_table = True
            table_buf.append(line)
            continue
        else:
            flush_table()
        # 图片
        m = IMG_OBSIDIAN.search(line) or IMG_MD.search(line)
        if m:
            name = m.group(1).split("|")[0].split("?")[0].strip()
            target = sub if sub is not None else cur
            if target is not None:
                target["images"].append(name)
            continue
        # bullet
        bl = re.match(r"^\s*[-*]\s+(.*)$", line)
        if bl and cur is not None:
            target = sub if sub is not None else cur
            target["bullets"].append(clean_md(bl.group(1)))
            continue
        # 水平分割线 (--- / *** / ___) 视为装饰，跳过
        if re.fullmatch(r"\s*([-*_])\s*(\1\s*){2,}", line):
            continue
        # 空行
        if not line.strip():
            continue
        # 首段（标题之前的正文）归 lead
        if cur is None:
            doc["lead"].append(clean_md(line))
        else:
            target = sub if sub is not None else cur
            target["paras"].append(clean_md(line))

    flush_table()
    return doc


def first_table(sec):
    """返回 (标题, 表头, 行) 或 None。章节级优先，其次第一个含表的子节。"""
    if sec["tables"]:
        h, d = sec["tables"][0]
        return (sec["heading"], h, d)
    for s in sec["subs"]:
        if s["tables"]:
            h, d = s["tables"][0]
            return (s["heading"], h, d)
    return None


def count_slides(doc):
    c = 2  # 封面 + Agenda
    for sec in doc["sections"]:
        c += 1  # 章节分隔页
        fu = len(sec["images"]) + sum(len(s["images"]) for s in sec["subs"])
        if fu > 0:
            c += max(1, fu)
            continue
        if first_table(sec) is not None:
            c += 1
            if [s for s in sec["subs"] if not s["tables"]]:
                c += 1
            continue
        if sec["subs"] or sec["bullets"]:
            c += 1
        else:
            c += 1
    return c


# ---------------- 图片工具 ----------------
def read_ratio(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
            return (w / h) if h else 0.8
    except Exception:
        return 0.8


def resolve_image(md_dir, name):
    cands = [os.path.join(md_dir, name), os.path.join(md_dir, "images", name)]
    for c in cands:
        if os.path.exists(c):
            return c
    for root, _, files in os.walk(md_dir):
        if name in files:
            return os.path.join(root, name)
    return None


def copy_images(doc, md_dir, out_img_dir, max_side=2000):
    os.makedirs(out_img_dir, exist_ok=True)
    for sec in doc["sections"]:
        names = list(sec["images"])
        names += [n for sub in sec["subs"] for n in sub["images"]]
        for name in names:
            src = resolve_image(md_dir, name)
            dst = os.path.join(out_img_dir, name)
            if not src:
                print("  [warn] 图片未找到，跳过:", name)
                continue
            try:
                from PIL import Image
                im = Image.open(src).convert("RGB")
                w, h = im.size
                if max(w, h) > max_side:
                    s = max_side / max(w, h)
                    im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
                im.save(dst, "PNG", optimize=True)
            except Exception:
                shutil.copy(src, dst)


# ---------------- 页面构建（通用）----------------
def s_cover(title, summary, authors=""):
    out = svg_open()
    out.append(f'<rect x="0" y="0" width="{W}" height="100" fill="{BLUE}"/>')
    out.append(f'<rect x="0" y="0" width="6" height="100" fill="{ORANGE}"/>')
    out.append(T(W - 40, 64, "浙江大学 · 求是创新", 16, FONT_CN, "#FFFFFF", "400", "end"))
    ty = 290
    for ln in wrap_text(title, 1080, FS_COVER_T):
        out.append(T(640, ty, ln, FS_COVER_T, FONT_EN, BLUE, "700", "middle"))
        ty += FS_COVER_T + 12
    out.append(f'<line x1="440" y1="{ty+30}" x2="840" y2="{ty+30}" stroke="{BLUE2}" stroke-width="2"/>')
    out.append(f'<circle cx="640" cy="{ty+30}" r="5" fill="{ORANGE}"/>')
    yy = ty + 64
    if summary:
        for ln in wrap_text(summary, 1000, FS_COVER_D):
            out.append(T(640, yy, ln, FS_COVER_D, FONT_CN, INK, "400", "middle"))
            yy += FS_COVER_D + 8
    if authors:
        out.append(T(640, 560, authors, 17, FONT_CN, GRAY, "400", "middle"))
    out.append(f'<rect x="0" y="665" width="{W}" height="55" fill="{PALE}"/>')
    out.append(T(640, 698, "组会汇报", 14, FONT_CN, GRAY, "400", "middle"))
    out.extend(svg_close(1, ""))
    return "\n".join(out), summary or title


def s_agenda(items):
    """items: list of (label, title, desc)"""
    out = []
    col_w = (CW - 30) // 2
    x0 = ML
    y0 = CTOP + 6
    rh = 120 if len(items) <= 6 else 92
    for i, (num, title, desc) in enumerate(items):
        col = i % 2
        row = i // 2
        x = x0 + col * (col_w + 30)
        y = y0 + row * rh
        out.append(f'<rect x="{x}" y="{y}" width="{col_w}" height="{rh-16}" rx="8" fill="{PALE}" stroke="{LINE}" stroke-width="1"/>')
        out.append(f'<rect x="{x}" y="{y}" width="6" height="{rh-16}" fill="{BLUE}"/>')
        out.append(f'<circle cx="{x+42}" cy="{y+38}" r="22" fill="{BLUE}"/>')
        out.append(T(x + 42, y + 45, num, 18, FONT_EN, "#FFFFFF", "700", "middle"))
        out.append(T(x + 78, y + 34, title, 19, FONT_CN, INK, "700"))
        para_box(desc, x + 78, y + 54, col_w - 92, 16, out, GRAY, "400", gap=0)
    return content_slide("", "汇报路线 · Agenda", "沿 md 分区组织汇报：背景 → 方法 → 结果 → 讨论 → 结论",
                          out, 2, "汇报路线"), (
        "汇报路线。整体按 md 的章节分区组织：" +
        "；".join(t for _, t, _ in items) + "。")


def s_divider(page_n, label, title, desc):
    out = svg_open()
    for x, o in [(1000, 0.35), (1050, 0.25), (1100, 0.18)]:
        out.append(f'<line x1="{x}" y1="120" x2="{x}" y2="620" stroke="{BLUE2}" stroke-width="1" stroke-opacity="{o}"/>')
    out.append(T(90, 500, label, 300, FONT_EN, LINE2, "700"))
    out.append(f'<rect x="0" y="0" width="6" height="{H}" fill="{ORANGE}"/>')
    out.append(T(100, 360, title, 56, FONT_CN, BLUE, "700"))
    out.append(T(100, 430, desc, 22, FONT_CN, GRAY, "400"))
    out.append(f'<rect x="100" y="462" width="80" height="5" fill="{ORANGE}" rx="2"/>')
    out.extend(svg_close(page_n, ""))
    return "\n".join(out)


def s_figure(sec_label, title, key_msg, purpose, panels, link, img_rel, img_ratio,
             page_n, section_name):
    out = []
    r = img_ratio or 0.8
    fw = int(FIG_H * r)
    fh = FIG_H
    fx = ML + (CW - 20 - fw) + 20
    tw = CW - 20 - fw
    fy = CTOP + (CH - FIG_H) // 2
    figure(img_rel, fx, fy, fw, fh, out)
    x = ML
    y = CTOP
    if purpose:
        y = tag(out, "实验目的", x, y)
        y = para_box(purpose, x, y, tw, FS_BODY2, out, INK, "400", gap=8)
        y += 4
    y = tag(out, "图意拆解", x, y)
    y = para_box_multi(panels, x, y, tw, FS_BODY2, out, INK, "400", gap=8)
    y += 4
    y = tag(out, "逻辑衔接", x, y, ORANGE)
    y = para_box(link, x, y, tw, FS_BODY2, out, GRAY, "400", gap=4)
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


def s_table(sec_label, title, key_msg, header, rows, page_n, section_name):
    out = []
    ncols = max(len(header), *(len(r) for r in rows if r))
    x0, y0 = ML, CTOP + 4
    widths = []
    if ncols == 2:
        widths = [220, CW - 220]
    else:
        base = CW // ncols
        widths = [base] * ncols
    # 表头
    cx = x0
    for j, h in enumerate(header[:ncols]):
        out.append(f'<rect x="{cx}" y="{y0}" width="{widths[j]}" height="36" fill="{BLUE}"/>')
        out.append(T(cx + 12, y0 + 24, h, 17, FONT_CN, "#FFFFFF", "700"))
        cx += widths[j]
    yy = y0 + 36
    rh = max(64, 700 // max(1, len(rows) + 1))
    for i, row in enumerate(rows):
        fill = "#FFFFFF" if i % 2 == 0 else PALE
        cx = x0
        for j in range(ncols):
            v = row[j] if j < len(row) else ""
            out.append(f'<rect x="{cx}" y="{yy}" width="{widths[j]}" height="{rh}" fill="{fill}" stroke="{LINE}" stroke-width="1"/>')
            if j == 0:
                out.append(T(cx + 12, yy + rh / 2 + 5, v, 16, FONT_CN, BLUE, "700"))
            else:
                para_box(v, cx + 12, yy + 8, widths[j] - 24, 16, out, INK, "400", gap=0)
            cx += widths[j]
        yy += rh
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


def s_cards(sec_label, title, key_msg, subs, page_n, section_name):
    out = []
    items = [(s["heading"], " ".join(s["paras"])) for s in subs]
    n = len(items)
    cols = 2 if n > 1 else 1
    rows = (n + cols - 1) // cols
    cw = (CW - 24) // cols
    avail = CH - 12
    ch = min(215, avail // rows - 14)
    for i, (h, body) in enumerate(items):
        col = i % cols
        row = i // cols
        x = ML + col * (cw + 24)
        y = CTOP + 6 + row * (ch + 14)
        out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="8" fill="#FFFFFF" stroke="{LINE}" stroke-width="1"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="34" rx="8" fill="{BLUE}"/>')
        out.append(f'<rect x="{x}" y="{y+17}" width="{cw}" height="17" fill="{BLUE}"/>')
        out.append(T(x + 14, y + 23, h, FS_CARD_H, FONT_CN, "#FFFFFF", "700"))
        if body:
            para_box(body, x + 16, y + 48, cw - 32, 17, out, INK, "400", gap=0)
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


def s_bullets(sec_label, title, key_msg, items, page_n, section_name):
    out = []
    bullets(items, ML, CTOP + 14, CW, FS_BULLET, out, gap=16)
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


def s_para(sec_label, title, key_msg, paras, page_n, section_name):
    out = []
    y = CTOP + 6
    for p in paras:
        y = para_box(p, ML, y, CW, FS_BODY, out, INK, "400", gap=8)
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


def strip_boiler(s):
    """去掉 md 自带的套话前缀（主干叙述：/作者指出：/本文首次…），避免机械腔。"""
    s = s.strip()
    for p in ("主干叙述：", "主干叙述:", "作者指出，", "作者指出:",
              "本文首次", "本文中首次", "值得注意的是，", "值得一提的是，"):
        if s.startswith(p):
            s = s[len(p):].strip()
    return s


def s_critique(sec_label, title, key_msg, items, page_n, section_name):
    out = []
    bullets([strip_boiler(it) for it in items], ML, CTOP + 14, CW, FS_BULLET, out, gap=20)
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


def s_conclusion(sec_label, title, key_msg, rows, page_n, section_name):
    out = []
    x0, y0 = ML, CTOP + 6
    c1, c2 = 220, CW - 220
    head_h, row_h = 44, 96
    out.append(f'<rect x="{x0}" y="{y0}" width="{c1}" height="{head_h}" fill="{BLUE}"/>')
    out.append(f'<rect x="{x0+c1}" y="{y0}" width="{c2}" height="{head_h}" fill="{BLUE}"/>')
    out.append(T(x0 + 12, y0 + head_h * 0.66, "维度", 17, FONT_CN, "#FFFFFF", "700"))
    out.append(T(x0 + c1 + 12, y0 + head_h * 0.66, "结论", 17, FONT_CN, "#FFFFFF", "700"))
    yy = y0 + head_h
    for i, (k, v) in enumerate(rows):
        fill = "#FFFFFF" if i % 2 == 0 else PALE
        out.append(f'<rect x="{x0}" y="{yy}" width="{c1}" height="{row_h}" fill="{fill}" stroke="{LINE}" stroke-width="1"/>')
        out.append(f'<rect x="{x0+c1}" y="{yy}" width="{c2}" height="{row_h}" fill="{fill}" stroke="{LINE}" stroke-width="1"/>')
        out.append(T(x0 + 12, yy + 34, k, 16, FONT_CN, BLUE, "700"))
        para_box(v, x0 + c1 + 12, yy + 8, c2 - 24, 17, out, INK, "400", gap=0)
        yy += row_h
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


def s_dataref(sec_label, title, key_msg, items, summary, page_n, section_name):
    out = []
    y = bullets(items, ML, CTOP + 14, CW, FS_BULLET, out, gap=18)
    out.append(f'<rect x="{ML}" y="{y+6}" width="{CW}" height="70" rx="6" fill="{PALE}"/>')
    out.append(f'<rect x="{ML}" y="{y+6}" width="6" height="70" fill="{ORANGE}"/>')
    para_box(summary, ML + 16, y + 22, CW - 32, 17, out, INK, "400", gap=0)
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


def s_flow(sec_label, title, key_msg, nodes, note, page_n, section_name):
    out = []
    bw, bh = 200, 66
    row1y, row2y = 245, 432
    k = len(nodes)
    top = nodes[: (k + 1) // 2]
    bot = nodes[(k + 1) // 2:]
    def xs(n_):
        if n_ <= 1:
            return [520]
        return [60 + i * (920 / (n_ - 1)) for i in range(n_)]
    topx = xs(len(top))
    if len(bot) == len(top) - 1:
        botx = list(reversed(topx[1:]))
    elif bot:
        botx = list(reversed(topx))
    else:
        botx = []
    cy1, cy2 = row1y + bh / 2, row2y + bh / 2
    edges = []
    for i in range(len(top) - 1):
        edges.append((topx[i] + bw, cy1, topx[i + 1], cy1))
    if bot:
        edges.append((topx[-1] + bw / 2, row1y + bh, topx[-1] + bw / 2, row2y))
        for i in range(len(bot) - 1):
            edges.append((botx[i], cy2, botx[i + 1] + bw, cy2))
    for (x1, y1, x2, y2) in edges:
        arrow(x1, y1, x2, y2, out)
    for i, nd in enumerate(top):
        draw_box(topx[i], row1y, bw, bh, nd, 16, out)
    for i, nd in enumerate(bot):
        draw_box(botx[i], row2y, bw, bh, nd, 16, out)
    out.append(f'<rect x="{ML}" y="560" width="{CW}" height="64" rx="6" fill="{PALE}"/>')
    out.append(f'<rect x="{ML}" y="560" width="6" height="64" fill="{BLUE2}"/>')
    para_box(note, ML + 16, 576, CW - 32, 17, out, INK, "400", gap=0)
    return content_slide(sec_label, title, key_msg, out, page_n, section_name)


# ---------------- 主流程 ----------------
def first_sentence(text):
    for sep in ("。", ".", "；", ";"):
        if sep in text:
            return text[:text.index(sep) + 1]
    return text


def build(doc, out_dir, title_override=None, authors=""):
    global TOTAL
    os.makedirs(os.path.join(out_dir, "svg_output"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "notes"), exist_ok=True)
    TOTAL = count_slides(doc)

    title = title_override or doc["title"] or "未命名汇报"
    summary = " ".join(doc["lead"][:2]) or (doc["sections"][0]["paras"][0] if doc["sections"] else "")
    sections = doc["sections"]

    slides = []  # (name, svg, note)
    n = 1

    svg, note = s_cover(title, summary, authors)
    slides.append((f"{n:02d}_cover", svg, note))
    n += 1

    agenda_items = []
    for i, sec in enumerate(sections, 1):
        desc = sec["paras"][0] if sec["paras"] else (sec["subs"][0]["paras"][0] if sec["subs"] else "")
        agenda_items.append((f"{i:02d}", sec["heading"], desc))
    svg, note = s_agenda(agenda_items)
    slides.append((f"{n:02d}_agenda", svg, note))
    n += 1

    for i, sec in enumerate(sections, 1):
        label = f"{i:02d}"
        sec_first = sec["paras"][0] if sec["paras"] else sec["heading"]
        svg = s_divider(n, label, sec["heading"], sec_first)
        slides.append((f"{n:02d}_divider_{i}", svg, None))
        n += 1

        # 图页单元：章节级图片 + 子节级图片（Vita 的图就在 ### 3.1-3.5 里）
        fig_units = [(None, img) for img in sec["images"]]
        for sub in sec["subs"]:
            for img in sub["images"]:
                fig_units.append((sub, img))
        if fig_units:
            for sub, img in fig_units:
                if sub is not None:
                    sec_label = f"{i}.{sec['subs'].index(sub) + 1}"
                    title = sub["heading"]
                    paras = sub["paras"] or [sec_first]
                else:
                    sec_label = label
                    title = sec["heading"]
                    paras = sec["paras"] or [sec_first]
                purpose = strip_boiler(paras[0])
                panels = [strip_boiler(p) for p in (paras[1:] if len(paras) > 1 else paras)]
                key = first_sentence(purpose)
                # 单句目的只放 key 条，避免左栏重复；多句时左栏再展开
                _parts = [p for p in re.split(r"[。.；;]", purpose) if p.strip()]
                purpose_left = purpose if len(_parts) > 1 else ""
                next_head = sections[i]["heading"] if i < len(sections) else ""
                link = f"→ 下一节：{next_head}" if next_head else "见全文结论"
                img_rel = "../images/" + img
                ratio = read_ratio(os.path.join(out_dir, "images", img))
                svg = s_figure(sec_label, title, key, purpose_left, panels, link,
                               img_rel, ratio, n, title)
                note = f"{title}。图{img}：{key} " + " ".join(panels) + " 逻辑衔接：" + link
                slides.append((f"{n:02d}_fig_{i}", svg, note))
                n += 1
            continue

        # 表格（章节级优先，其次含表的子节）
        tbl = first_table(sec)
        if tbl is not None:
            ttitle, theader, trows = tbl
            svg = s_table(label, ttitle, first_sentence(sec_first), theader, trows, n, ttitle)
            slides.append((f"{n:02d}_table_{i}", svg, f"{ttitle}。表格共 {len(trows)} 行。"))
            n += 1
            subs_left = [s for s in sec["subs"] if not s["tables"]]
            if subs_left:
                svg = s_cards(label, sec["heading"], first_sentence(sec_first), subs_left, n, sec["heading"])
                slides.append((f"{n:02d}_cards_{i}", svg, f"{sec['heading']}。含 {len(subs_left)} 个子小节。"))
                n += 1
            continue

        if sec["subs"]:
            svg = s_cards(label, sec["heading"], first_sentence(sec_first), sec["subs"], n, sec["heading"])
            slides.append((f"{n:02d}_cards_{i}", svg, f"{sec['heading']}。含 {len(sec['subs'])} 个子小节。"))
            n += 1
        elif sec["bullets"]:
            svg = s_bullets(label, sec["heading"], first_sentence(sec_first), [strip_boiler(b) for b in sec["bullets"]], n, sec["heading"])
            slides.append((f"{n:02d}_bullets_{i}", svg, f"{sec['heading']}。{len(sec['bullets'])} 条要点。"))
            n += 1
        else:
            svg = s_para(label, sec["heading"], first_sentence(sec_first), [strip_boiler(p) for p in sec["paras"]], n, sec["heading"])
            slides.append((f"{n:02d}_para_{i}", svg, f"{sec['heading']}。" + " ".join(sec["paras"][:2])))
            n += 1

    # 写入
    for name, svg, note in slides:
        with open(os.path.join(out_dir, "svg_output", name + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        if note:
            with open(os.path.join(out_dir, "notes", name + ".md"), "w", encoding="utf-8") as f:
                f.write(note)
    return slides


# ---------------- 编排层（curation）：达到旧版叙事效果 ----------------
def load_curation(path):
    """读取编排数据 JSON（或 YAML）。结构见仓库 references/md_driven_content.md §10。"""
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
            return yaml.safe_load(txt)
        except Exception:
            pass
    import json
    return json.loads(txt)


def count_section_slides(sec):
    fu = len(sec["images"]) + sum(len(s["images"]) for s in sec["subs"])
    if fu > 0:
        return max(1, fu)
    if sec["subs"]:
        n = 0
        if first_table(sec) is not None:
            n += 1
        if any(not s["tables"] for s in sec["subs"]):
            n += 1
        return max(1, n)
    if first_table(sec) is not None:
        return 1
    if sec["bullets"]:
        return 1
    return 1


def build_curated(doc, curation, out_dir, title_override=None, authors=""):
    """按 curation 编排出叙事化 deck（旧版 18 页质感）。

    curation 字段：
      cover:        {summary,title,authors}      封面覆盖
      chapters:     [{label,title,desc,sections:[idx...]}]  章边界插分隔页
      roles:        {idx: background/flow/result/methods/discussion/critique/conclusion/dataref}
      results:      {img.png: {title,finding,purpose,panels[],link}}   结果页四段式
      flows:        {idx: {nodes[],note}}          流程图（如策略页）
      conclusion:    {rows:[[k,v]...]}             结论两列表
      dataref:      {items[],summary}              数据速查
      background:    {cards:[[h,body]...]}         背景卡片（可选，缺则取 md 子节）
      discussion:    {items:[]} / critique: {items:[]}   （可选，缺则取 md）
    """
    global TOTAL
    sections = doc["sections"]
    chapters = curation.get("chapters", [])
    roles = {str(k): v for k, v in curation.get("roles", {}).items()}
    results = curation.get("results", {})
    flows = curation.get("flows", {})
    conclusion = curation.get("conclusion", {})
    dataref = curation.get("dataref", {})
    cover_cfg = curation.get("cover", {})

    # 总页数（页脚用）
    member = set()
    for ch in chapters:
        for idx in ch.get("sections", []):
            member.add(int(idx))
    TOTAL = 2  # 封面 + Agenda
    for ch in chapters:
        TOTAL += 1  # 分隔页
        for idx in ch.get("sections", []):
            TOTAL += count_section_slides(sections[idx - 1])
    for idx in range(1, len(sections) + 1):
        if idx in member:
            continue
        TOTAL += count_section_slides(sections[idx - 1])

    title = title_override or cover_cfg.get("title") or doc["title"] or "未命名汇报"
    summary = (cover_cfg.get("summary")
               or first_sentence(" ".join(doc["lead"][:2]))
               or (sections[0]["paras"][0] if sections and sections[0]["paras"] else ""))
    authors = authors or cover_cfg.get("authors") or doc.get("authors", "")

    slides = []
    n = 1

    svg, note = s_cover(title, summary, authors)
    slides.append((f"{n:02d}_cover", svg, note)); n += 1

    cur_agenda = curation.get("agenda")
    if cur_agenda:
        agenda_items = [(a[0], a[1], a[2]) for a in cur_agenda]
    else:
        agenda_items = []
        for i, sec in enumerate(sections, 1):
            d0 = sec["paras"][0] if sec["paras"] else (sec["subs"][0]["paras"][0] if sec["subs"] else "")
            agenda_items.append((f"{i:02d}", sec["heading"], d0))
    svg, note = s_agenda(agenda_items)
    slides.append((f"{n:02d}_agenda", svg, note)); n += 1

    def render_section(idx, sec):
        nonlocal n
        role = roles.get(str(idx), "auto")
        # 结果页：章节/子节含图
        fig_units = [(None, img) for img in sec["images"]]
        for sub in sec["subs"]:
            for img in sub["images"]:
                fig_units.append((sub, img))
        if fig_units:
            for sub, img in fig_units:
                if img in results:
                    r = results[img]
                    sec_label = (f"{idx}.{sec['subs'].index(sub) + 1}"
                                 if sub is not None else f"{idx:02d}")
                    title_r = r.get("title", (sub or sec)["heading"])
                    finding = r.get("finding", "")
                    purpose = r.get("purpose", "")
                    panels = r.get("panels", [])
                    link = r.get("link", "")
                    ratio = read_ratio(os.path.join(out_dir, "images", img))
                    svg = s_figure(sec_label, title_r, finding, purpose, panels, link,
                                   "../images/" + img, ratio, n, title_r)
                    note = f"{title_r}。{finding} " + " ".join(panels) + " 逻辑衔接：" + link
                else:
                    paras = (sub or sec)["paras"] or [sec["heading"]]
                    purpose = strip_boiler(paras[0])
                    panels = [strip_boiler(p) for p in paras[1:]] or paras
                    sec_label = (f"{idx}.{sec['subs'].index(sub) + 1}"
                                 if sub is not None else f"{idx:02d}")
                    ratio = read_ratio(os.path.join(out_dir, "images", img))
                    svg = s_figure(sec_label, (sub or sec)["heading"], first_sentence(purpose),
                                   purpose, panels, "→ 下一节", "../images/" + img, ratio, n,
                                   (sub or sec)["heading"])
                    note = f"{(sub or sec)['heading']}。"
                slides.append((f"{n:02d}_fig", svg, note)); n += 1
            return
        # 流程图
        if role == "flow" or str(idx) in flows:
            spec = flows.get(str(idx), {})
            svg = s_flow(f"{idx:02d}", sec["heading"],
                         "模板酶→基序抽取→生成式共设计→实验验证，形成“设计即验证”闭环",
                         spec.get("nodes", []), spec.get("note", ""), n, sec["heading"])
            slides.append((f"{n:02d}_strategy", svg, spec.get("note", ""))); n += 1
            return
        # 背景卡片（curation 优先）
        if role == "background":
            cards = curation.get("background", {}).get("cards")
            if cards:
                subs = [{"heading": h, "paras": [b]} for h, b in cards]
                svg = s_cards(f"{idx:02d}", sec["heading"], first_sentence(sec["heading"]),
                              subs, n, sec["heading"])
                slides.append((f"{n:02d}_cards", svg, f"{sec['heading']}")); n += 1
                return
        # 结论表
        if role == "conclusion":
            svg = s_conclusion(f"{idx:02d}", sec["heading"], first_sentence(sec["heading"]),
                               conclusion.get("rows", []), n, sec["heading"])
            slides.append((f"{n:02d}_conclusion", svg, "结论速查")); n += 1
            return
        # 数据速查
        if role == "dataref":
            svg = s_dataref(f"{idx:02d}", sec["heading"], first_sentence(sec["heading"]),
                            dataref.get("items", []), dataref.get("summary", ""), n, sec["heading"])
            slides.append((f"{n:02d}_dataref", svg, "数据速查")); n += 1
            return
        # 批判
        if role == "critique":
            items = (curation.get("critique", {}).get("items")
                     or sec["bullets"] or sec["paras"])
            svg = s_critique(f"{idx:02d}", sec["heading"], first_sentence(" ".join(items[:1])),
                             items, n, sec["heading"])
            slides.append((f"{n:02d}_critique", svg, "批判")); n += 1
            return
        # 讨论
        if role == "discussion":
            items = (curation.get("discussion", {}).get("items")
                     or sec["bullets"] or sec["paras"])
            svg = s_bullets(f"{idx:02d}", sec["heading"], first_sentence(" ".join(items[:1])),
                            items, n, sec["heading"])
            slides.append((f"{n:02d}_discussion", svg, "讨论")); n += 1
            return
        # 方法：优先用 curation 的 materials / protocols
        if role == "methods":
            mat = curation.get("materials")
            if mat:
                svg = s_table(mat.get("sec_label", f"{idx:02d}"),
                              mat.get("title", sec["heading"]),
                              mat.get("key_msg", ""),
                              mat.get("header", ["类别", "说明"]),
                              mat.get("rows", []), n,
                              mat.get("section_name", sec["heading"]))
                slides.append((f"{n:02d}_table", svg, f"{mat.get('title','')}")); n += 1
            prot = curation.get("protocols")
            if prot:
                subs = [{"heading": h, "paras": [b]} for h, b in prot.get("cards", [])]
                svg = s_cards(prot.get("sec_label", f"{idx:02d}"),
                              prot.get("title", sec["heading"]),
                              prot.get("key_msg", ""), subs, n,
                              prot.get("section_name", sec["heading"]))
                slides.append((f"{n:02d}_cards", svg, f"{prot.get('title','')}")); n += 1
            return
        # 背景 / 自动：表格 + 卡片
        if sec["subs"]:
            tbl = first_table(sec)
            if tbl is not None:
                ttitle, theader, trows = tbl
                svg = s_table(f"{idx:02d}", ttitle, first_sentence(sec["heading"]),
                              theader, trows, n, ttitle)
                slides.append((f"{n:02d}_table", svg, f"{ttitle}")); n += 1
                subs_left = [s for s in sec["subs"] if not s["tables"]]
                if subs_left:
                    svg = s_cards(f"{idx:02d}", sec["heading"], first_sentence(sec["heading"]),
                                  subs_left, n, sec["heading"])
                    slides.append((f"{n:02d}_cards", svg, f"{sec['heading']}")); n += 1
            else:
                svg = s_cards(f"{idx:02d}", sec["heading"], first_sentence(sec["heading"]),
                              sec["subs"], n, sec["heading"])
                slides.append((f"{n:02d}_cards", svg, f"{sec['heading']}")); n += 1
            return
        if sec["bullets"]:
            svg = s_bullets(f"{idx:02d}", sec["heading"], first_sentence(sec["heading"]),
                            [strip_boiler(b) for b in sec["bullets"]], n, sec["heading"])
            slides.append((f"{n:02d}_bullets", svg, f"{sec['heading']}")); n += 1
            return
        svg = s_para(f"{idx:02d}", sec["heading"], first_sentence(sec["heading"]),
                     [strip_boiler(p) for p in sec["paras"]], n, sec["heading"])
        slides.append((f"{n:02d}_para", svg, f"{sec['heading']}")); n += 1

    # 不属于任何章的节（intro，无分隔页），按 doc 顺序在前
    for idx in range(1, len(sections) + 1):
        if idx in member:
            continue
        render_section(idx, sections[idx - 1])
    # 章：分隔页 + 成员节
    for ch in chapters:
        svg = s_divider(n, ch.get("label", ""), ch["title"], ch.get("desc", ""))
        slides.append((f"{n:02d}_divider", svg, None)); n += 1
        for idx in ch.get("sections", []):
            render_section(idx, sections[idx - 1])

    os.makedirs(os.path.join(out_dir, "svg_output"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "notes"), exist_ok=True)
    for name, svg, note in slides:
        with open(os.path.join(out_dir, "svg_output", name + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        if note:
            with open(os.path.join(out_dir, "notes", name + ".md"), "w", encoding="utf-8") as f:
                f.write(note)
    return slides


def main():
    ap = argparse.ArgumentParser(description="Markdown → 学术组会 PPT (SVG)")
    ap.add_argument("input", help="源 Markdown 文件路径")
    ap.add_argument("--out", default=None, help="输出目录（默认 <md名>_ppt）")
    ap.add_argument("--title", default=None, help="封面标题覆盖")
    ap.add_argument("--authors", default="", help="封面作者行")
    ap.add_argument("--curation", default=None,
                    help="编排数据 JSON/YAML（章节/结果四段式/版式分化），达到旧版叙事效果")
    args = ap.parse_args()

    md_path = os.path.abspath(args.input)
    md_dir = os.path.dirname(md_path)
    out_dir = args.out or (os.path.splitext(md_path)[0] + "_ppt")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    doc = parse_md(md_path)
    copy_images(doc, md_dir, os.path.join(out_dir, "images"))
    if args.curation:
        curation = load_curation(args.curation)
        slides = build_curated(doc, curation, out_dir, title_override=args.title,
                               authors=args.authors or doc.get("authors", ""))
    else:
        slides = build(doc, out_dir, title_override=args.title,
                       authors=args.authors or doc.get("authors", ""))
    print(f"Generated {len(slides)} slides -> {out_dir}")
    for name, _, _ in slides:
        print(" -", name)


if __name__ == "__main__":
    main()
