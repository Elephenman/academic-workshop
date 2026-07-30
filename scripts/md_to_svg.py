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

输出 DIR/ 下：svg_output/*.svg（每页一文件）、images/*.png（拷贝+必要时降采样）、notes/*.md（演讲备注）。
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
    """去除 Markdown 强调标记（**粗体** / *斜体* / __ / `代码`），避免泄漏进 PPT。"""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"\1", s)
    s = re.sub(r"__(.+?)__", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
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
    return s.strip().strip("|").strip()


def parse_md(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    doc = {"title": None, "sections": [], "lead": []}
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
                purpose = paras[0]
                panels = paras[1:] if len(paras) > 1 else paras
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
            svg = s_bullets(label, sec["heading"], first_sentence(sec_first), sec["bullets"], n, sec["heading"])
            slides.append((f"{n:02d}_bullets_{i}", svg, f"{sec['heading']}。{len(sec['bullets'])} 条要点。"))
            n += 1
        else:
            svg = s_para(label, sec["heading"], first_sentence(sec_first), sec["paras"], n, sec["heading"])
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


def main():
    ap = argparse.ArgumentParser(description="Markdown → 学术组会 PPT (SVG)")
    ap.add_argument("input", help="源 Markdown 文件路径")
    ap.add_argument("--out", default=None, help="输出目录（默认 <md名>_ppt）")
    ap.add_argument("--title", default=None, help="封面标题覆盖")
    ap.add_argument("--authors", default="", help="封面作者行")
    args = ap.parse_args()

    md_path = os.path.abspath(args.input)
    md_dir = os.path.dirname(md_path)
    out_dir = args.out or (os.path.splitext(md_path)[0] + "_ppt")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    doc = parse_md(md_path)
    copy_images(doc, md_dir, os.path.join(out_dir, "images"))
    slides = build(doc, out_dir, title_override=args.title, authors=args.authors)
    print(f"Generated {len(slides)} slides -> {out_dir}")
    for name, _, _ in slides:
        print(" -", name)


if __name__ == "__main__":
    main()
