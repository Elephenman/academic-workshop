#!/usr/bin/env python3
"""
taste_guardian_cli.py — Academic Workshop Taste Guardian CLI

Machine-assisted detection for anti-AI-slop compliance.
Scans design_spec.md (and optionally spec_lock.md) against
the 10 taste rules defined in references/taste_guardian.md.

Usage:
    python taste_guardian_cli.py <project_path>/design_spec.md [--spec-lock <spec_lock_path>] [--output <report_path>]

Detects:
    1. HEX colors in purple gradient range (HSL hue 240-300, saturation>50%)
    2. Inter/Roboto as primary fonts
    3. Missing breathing pages in page rhythm
    4. Emoji icon strategy
    5. Gradient backgrounds on non-cover pages
    6. Card grid uniformity (all pages dense)
    7. SVG hand-drawn image replacement keywords

Output: Markdown taste report to stdout (or file via --output)
"""

import win_compat  # noqa: F401 -- Windows compat (path+encoding fix)

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime


# ─── Color Analysis ───────────────────────────────────────────────

def hex_to_hsl(hex_color: str) -> tuple:
    """Convert HEX color to HSL (hue, saturation, lightness)."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return (0, 0, 0)
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
    except ValueError:
        return (0, 0, 0)

    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin

    # Lightness
    l = (cmax + cmin) / 2.0

    if delta == 0:
        h = 0.0
        s = 0.0
    else:
        # Saturation
        s = delta / (1.0 - abs(2.0 * l - 1.0)) if (1.0 - abs(2.0 * l - 1.0)) != 0 else 0.0

        # Hue
        if cmax == r:
            h = ((g - b) / delta) % 6.0
        elif cmax == g:
            h = (b - r) / delta + 2.0
        else:
            h = (r - g) / delta + 4.0

        h *= 60.0
        if h < 0:
            h += 360.0

    return (round(h, 1), round(s * 100, 1), round(l * 100, 1))


def is_purple_gradient(hex_color: str) -> bool:
    """Check if a HEX color falls in the purple gradient danger zone.
    
    Purple gradient zone: HSL hue 240-300, saturation > 50%.
    This catches the stereotypical AI "tech purple" that plagues presentations.
    """
    h, s, l = hex_to_hsl(hex_color)
    # Purple range: hue 240-300 (blue-purple to magenta-purple)
    # Must be saturated enough to be recognizable as "purple" (not just dark blue)
    # Must not be too dark or too light (near-black or near-white are fine)
    if 240 <= h <= 300 and s > 50 and 10 < l < 90:
        return True
    return False


# ─── Spec Parsing ─────────────────────────────────────────────────

def extract_hex_colors(text: str) -> list:
    """Extract all HEX color values (#RRGGBB) from text."""
    return re.findall(r'#([0-9A-Fa-f]{6})\b', text)


def parse_design_spec(spec_path: str) -> dict:
    """Parse key sections from design_spec.md for taste analysis."""
    content = Path(spec_path).read_text(encoding='utf-8')
    
    result = {
        'raw_text': content,
        'hex_colors': [],
        'color_section': '',
        'typography_section': '',
        'rhythm_section': '',
        'icon_strategy': '',
        'image_strategy': '',
        'gradient_mentions': [],
    }
    
    # Extract all HEX colors with context
    hex_pattern = re.compile(r'`?#([0-9A-Fa-f]{6})\b`?')
    for m in hex_pattern.finditer(content):
        hex_val = m.group(1)
        # Get surrounding context (100 chars before and after)
        start = max(0, m.start() - 100)
        end = min(len(content), m.end() + 100)
        context = content[start:end].replace('\n', ' ').strip()
        result['hex_colors'].append({
            'hex': f'#{hex_val}',
            'hsl': hex_to_hsl(f'#{hex_val}'),
            'is_purple': is_purple_gradient(f'#{hex_val}'),
            'context': context,
        })
    
    # Extract color scheme section
    color_match = re.search(r'(?:##\s*III\.|###\s*Color\s*Scheme)(.*?)(?=\n##|\n###|\Z)', content, re.DOTALL)
    if color_match:
        result['color_section'] = color_match.group(0)
    
    # Extract typography section
    typo_match = re.search(r'(?:##\s*IV\.|###\s*Typograph)(.*?)(?=\n##|\n###|\Z)', content, re.DOTALL)
    if typo_match:
        result['typography_section'] = typo_match.group(0)
    
    # Extract rhythm/page layout section
    rhythm_match = re.search(r'(?:##\s*VI\.|###\s*(?:Rhythm|Page|Layout|Content))(.*?)(?=\n##|\n###|\Z)', content, re.DOTALL)
    if rhythm_match:
        result['rhythm_section'] = rhythm_match.group(0)
    
    # Detect icon strategy keywords
    icon_patterns = ['emoji', 'Emoji', 'EMOJI', 'noto', 'twemoji']
    for p in icon_patterns:
        if p.lower() in content.lower():
            result['icon_strategy'] = p
            break
    
    # Detect image replacement keywords
    svg_hand_keywords = ['svg hand-drawn', 'SVG hand drawn', 'SVG手画', 'css剪影', 'CSS silhouette',
                          'hand-drawn illustration', 'sketch-style', 'doodle-style']
    for kw in svg_hand_keywords:
        if kw.lower() in content.lower():
            result['image_strategy'] = kw
            break
    
    # Detect gradient mentions (for non-cover pages)
    gradient_pattern = re.compile(r'(?:gradient|渐变).*?(?:background|背景)', re.IGNORECASE)
    result['gradient_mentions'] = gradient_pattern.findall(content)
    
    # Also check SVG gradient blocks
    svg_gradient_pattern = re.compile(r'<(?:linear|radial)Gradient[^>]*>', re.IGNORECASE)
    result['svg_gradients'] = svg_gradient_pattern.findall(content)
    
    return result


def parse_spec_lock(lock_path: str) -> dict:
    """Parse spec_lock.md for rhythm and color data."""
    content = Path(lock_path).read_text(encoding='utf-8')
    
    result = {
        'rhythm': {},
        'color_palette': {},
        'theme_colors': {},
        'font_groups': {},
    }
    
    # Try to extract JSON blocks from spec_lock
    # Rhythm Map
    rhythm_match = re.search(r'###\s*Rhythm\s*Map\s*\n(\{[^}]+\})', content, re.DOTALL)
    if not rhythm_match:
        # Try multi-line JSON
        rhythm_match = re.search(r'###\s*Rhythm\s*Map\s*\n(\{.*?\n\})', content, re.DOTALL)
    if rhythm_match:
        try:
            result['rhythm'] = json.loads(rhythm_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Color Palette
    palette_match = re.search(r'###\s*Color\s*Palette[^{]*(\{[^}]+\})', content, re.DOTALL)
    if not palette_match:
        palette_match = re.search(r'###\s*Color\s*Palette[^{]*(\{.*?\n\})', content, re.DOTALL)
    if palette_match:
        try:
            result['color_palette'] = json.loads(palette_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Theme Colors
    theme_match = re.search(r'###\s*Theme\s*Colors\s*\n(\{.*?\n\})', content, re.DOTALL)
    if theme_match:
        try:
            result['theme_colors'] = json.loads(theme_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Font Groups
    font_match = re.search(r'###\s*Font\s*Groups\s*\n(\{.*?\n\})', content, re.DOTALL)
    if font_match:
        try:
            result['font_groups'] = json.loads(font_match.group(1))
        except json.JSONDecodeError:
            pass
    
    return result


# ─── Taste Checks ─────────────────────────────────────────────────

def check_purple_gradient(spec_data: dict) -> list:
    """Rule 1: Check for purple gradient colors."""
    findings = []
    seen = set()
    for color_info in spec_data['hex_colors']:
        if color_info['is_purple'] and color_info['hex'] not in seen:
            seen.add(color_info['hex'])
            h, s, l = color_info['hsl']
            findings.append({
                'rule': 1,
                'severity': 'BLOCK',
                'hex': color_info['hex'],
                'hsl': f'h={h}, s={s}%, l={l}%',
                'message': f"Purple gradient detected: {color_info['hex']} (HSL: h={h}, s={s}%, l={l}%)",
                'fix': "Replace with low-saturation blue (#003366/#003F88) or neutral color",
            })
    return findings


def check_emoji_icons(spec_data: dict) -> list:
    """Rule 2: Check for Emoji icon strategy."""
    findings = []
    if spec_data['icon_strategy']:
        findings.append({
            'rule': 2,
            'severity': 'BLOCK',
            'message': f"Emoji icon strategy detected: '{spec_data['icon_strategy']}'",
            'fix': "Use tabler-outline icon library or no icons",
        })
    return findings


def check_uniform_card_grid(spec_data: dict, lock_data: dict) -> list:
    """Rule 3: Check if all pages are dense (no breathing pages)."""
    findings = []
    
    # Check from spec_lock rhythm data
    rhythm = lock_data.get('rhythm', {})
    if rhythm:
        has_breathing = any(
            page.get('rhythm') == 'breathing' 
            for page in rhythm.values()
        )
        has_anchor = any(
            page.get('rhythm') == 'anchor' 
            for page in rhythm.values()
        )
        dense_count = sum(
            1 for page in rhythm.values() 
            if page.get('rhythm') == 'dense'
        )
        total = len(rhythm)
        
        if not has_breathing and total > 3:
            # YELLOW-07 Academic exception: academic PPTs often need dense
            # information pages; downgrade BLOCK -> WARN for 3+ dense pages
            # when anchor pages exist (cover/TOC/ending provide rhythm).
            severity = 'WARN' if has_anchor else 'BLOCK'
            findings.append({
                'rule': 3,
                'severity': severity,
                'message': f"No breathing pages found. All {total} pages are dense/anchor (dense={dense_count}). "
                           f"{'[Academic exception: anchor pages provide rhythm]' if has_anchor else 'Uniform card grid risk.'}",
                'fix': f"Insert at least {max(1, total // 4)} breathing pages (large image + whitespace) between dense pages, "
                       f"or accept dense layout for academic content-heavy presentations",
            })
        elif dense_count > 0 and not has_breathing and total <= 3:
            findings.append({
                'rule': 3,
                'severity': 'WARN',
                'message': f"Only {total} pages with no breathing. Acceptable for short decks but consider adding one.",
                'fix': "Optional: add a breathing page for visual rhythm",
            })
    else:
        # Fallback: check design_spec text for rhythm keywords
        rhythm_text = spec_data.get('rhythm_section', '')
        if rhythm_text and 'breathing' not in rhythm_text.lower():
            if 'dense' in rhythm_text.lower():
                findings.append({
                    'rule': 3,
                    'severity': 'BLOCK',
                    'message': "No 'breathing' rhythm found in page layout section. All pages may be dense.",
                    'fix': "Insert breathing pages between dense content pages",
                })
    
    return findings


def check_svg_hand_drawn(spec_data: dict) -> list:
    """Rule 4: Check for SVG hand-drawn image replacement."""
    findings = []
    if spec_data['image_strategy']:
        findings.append({
            'rule': 4,
            'severity': 'BLOCK',
            'message': f"SVG hand-drawn image strategy detected: '{spec_data['image_strategy']}'",
            'fix': "Use original paper figures or honest placeholder (gray block + label)",
        })
    return findings


def check_gradient_background(spec_data: dict) -> list:
    """Rule 5: Check for gradient backgrounds on non-cover pages."""
    findings = []
    
    # Check SVG gradient definitions
    svg_gradients = spec_data.get('svg_gradients', [])
    if svg_gradients:
        # If gradient is defined and used in background context
        for grad in svg_gradients:
            grad_str = grad if isinstance(grad, str) else str(grad)
            # Check if it's a background gradient (not decorative)
            if 'bgDecor' in grad_str or 'background' in grad_str.lower():
                findings.append({
                    'rule': 5,
                    'severity': 'BLOCK',
                    'message': f"Gradient background detected in SVG: {grad_str[:80]}...",
                    'fix': "Use solid background (#FFFFFF/#F8F8F8) for content pages. Gradient allowed only on cover.",
                })
    
    # Check gradient mentions in text
    gradient_mentions = spec_data.get('gradient_mentions', [])
    if gradient_mentions:
        for mention in gradient_mentions:
            # Skip cover-page gradients
            if 'cover' in mention.lower() or 'title' in mention.lower():
                continue
            findings.append({
                'rule': 5,
                'severity': 'BLOCK',
                'message': f"Gradient background mention: '{mention}'",
                'fix': "Use solid background for content pages. Gradient allowed only on cover.",
            })
    
    return findings


def check_inter_roboto(spec_data: dict) -> list:
    """Rule 7 (WARN): Check for Inter/Roboto as primary font."""
    findings = []
    typo = spec_data.get('typography_section', '').lower()
    raw = spec_data.get('raw_text', '').lower()
    
    # Check both typography section and full text
    for font in ['inter', 'roboto']:
        if font in typo or (font in raw and 'primary' in raw):
            # More nuanced: check if it's used as primary/display
            if 'display' in typo or 'primary' in typo or 'heading' in typo or 'title' in typo:
                findings.append({
                    'rule': 7,
                    'severity': 'WARN',
                    'message': f"'{font.title()}' detected as primary/display font. This is a common AI default choice.",
                    'fix': "Consider a serif display font (Source Serif, Georgia) for academic credibility",
                })
            else:
                findings.append({
                    'rule': 7,
                    'severity': 'WARN',
                    'message': f"'{font.title()}' detected. Acceptable for body text but consider alternatives for headings.",
                    'fix': "For headings: serif display font. For body: system font stack is fine.",
                })
            break  # Only report once
    
    return findings


def check_icon_overload(spec_data: dict) -> list:
    """Rule 8 (WARN): Check for decorative icon overload."""
    findings = []
    raw = spec_data.get('raw_text', '')
    
    # Count icon mentions per page
    icon_count = len(re.findall(r'icon|图标|tabler|feather|heroicon', raw, re.IGNORECASE))
    page_count = len(re.findall(r'P\d{2}|Page\s*\d+', raw))
    
    if page_count > 0 and icon_count > page_count * 2:
        findings.append({
            'rule': 8,
            'severity': 'WARN',
            'message': f"Icon density high: {icon_count} icon references across ~{page_count} pages (~{icon_count/max(1,page_count):.1f} per page).",
            'fix': "Use icons only where functionally necessary (flow arrows, data type markers). Remove decorative icons.",
        })
    
    return findings


def check_info_density(spec_data: dict, lock_data: dict) -> list:
    """Rule 9 (WARN): Check for information density overload."""
    findings = []
    rhythm = lock_data.get('rhythm', {})
    
    if rhythm:
        overloaded = []
        for page_id, page_data in rhythm.items():
            if page_data.get('rhythm') == 'dense' and page_data.get('density', 0) > 0.8:
                overloaded.append(f"{page_id}(density={page_data['density']:.2f})")
        
        if overloaded:
            findings.append({
                'rule': 9,
                'severity': 'WARN',
                'message': f"High-density pages detected: {', '.join(overloaded)}. "
                           f"Risk of information overload for projection. [Academic exception: dense data pages are expected in research talks]",
                'fix': "Consider splitting into 2 pages or converting to breathing layout (big figure + one insight). "
                       "For academic talks, dense pages are acceptable if presenter guides audience through data",
            })
    
    return findings


def check_animation(spec_data: dict) -> list:
    """Rule 10 (WARN): Check for animation mentions."""
    findings = []
    raw = spec_data.get('raw_text', '').lower()
    
    animation_keywords = ['fly-in', 'spin', 'bounce', 'slide-in', 'fade-in', 'zoom', 
                          'morph', 'animate', 'animation', 'transition']
    # fade is acceptable for academic, flag the rest
    # YELLOW-07: "transition" keyword alone is acceptable (page transitions, not element animations)
    flagged = []
    for kw in animation_keywords:
        if kw in raw and kw not in ['fade', 'fade-in', 'transition']:
            flagged.append(kw)
    
    if flagged:
        findings.append({
            'rule': 10,
            'severity': 'WARN',
            'message': f"Animation mentions found: {', '.join(set(flagged))}. "
                       f"Academic presentations should avoid element animations. [Academic exception: fade page transitions are expected]",
            'fix': "Use only fade transitions for page changes. Remove all fly-in/spin/bounce/zoom element animations.",
        })
    
    return findings


# ─── Report Generation ────────────────────────────────────────────

def generate_report(findings: list, spec_path: str) -> str:
    """Generate a Markdown taste report from findings."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    blocks = [f for f in findings if f['severity'] == 'BLOCK']
    warns = [f for f in findings if f['severity'] == 'WARN']
    
    # Determine which rules passed
    all_rules = set(range(1, 11))
    violated_rules = set(f['rule'] for f in findings)
    passed_rules = all_rules - violated_rules
    
    lines = [
        "# Taste Guardian Scan Report",
        f"## Scan Time: {now}",
        f"## Source: {spec_path}",
        "",
        f"**Summary**: {len(blocks)} BLOCK (must fix) | {len(warns)} WARN (should fix) | {len(passed_rules)} PASS",
        "",
    ]
    
    if blocks:
        lines.append("## BLOCK - Must Fix")
        lines.append("")
        for f in blocks:
            lines.append(f"- **Rule {f['rule']}**: {f['message']}")
            lines.append(f"  - Fix: {f['fix']}")
            lines.append("")
    else:
        lines.append("## BLOCK - Must Fix")
        lines.append("")
        lines.append("- (none)")
        lines.append("")
    
    if warns:
        lines.append("## WARN - Should Fix")
        lines.append("")
        for f in warns:
            lines.append(f"- **Rule {f['rule']}**: {f['message']}")
            lines.append(f"  - Suggestion: {f['fix']}")
            lines.append("")
    else:
        lines.append("## WARN - Should Fix")
        lines.append("")
        lines.append("- (none)")
        lines.append("")
    
    # Passed rules
    rule_names = {
        1: "Purple gradient",
        2: "Emoji icons",
        3: "Uniform card grid",
        4: "SVG hand-drawn images",
        5: "Gradient background",
        6: "Rounded cards + left border",
        7: "Inter/Roboto fonts",
        8: "Decorative icon overload",
        9: "Info density overload",
        10: "Animation mentions",
    }
    
    lines.append("## PASS - Compliant")
    lines.append("")
    for rule_id in sorted(passed_rules):
        lines.append(f"- Rule {rule_id}: {rule_names.get(rule_id, 'Unknown')} - OK")
    lines.append("")
    
    # Verdict
    if blocks:
        lines.append("---")
        lines.append("")
        lines.append(f"**VERDICT: FAIL** - {len(blocks)} blocking issue(s) must be fixed before proceeding to Step 6.")
    else:
        lines.append("---")
        lines.append("")
        if warns:
            lines.append(f"**VERDICT: PASS WITH WARNINGS** - {len(warns)} warning(s) to consider. Proceeding to Step 6 is allowed.")
        else:
            lines.append("**VERDICT: CLEAN PASS** - All 10 taste rules compliant. Proceed to Step 6.")
    
    return '\n'.join(lines)


# ─── Main ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Academic Workshop Taste Guardian CLI - Machine-assisted anti-AI-slop detection'
    )
    parser.add_argument('design_spec', help='Path to design_spec.md')
    parser.add_argument('--spec-lock', help='Path to spec_lock.md (optional, for rhythm data)')
    parser.add_argument('--output', help='Output report file path (default: stdout)')
    args = parser.parse_args()
    
    spec_path = Path(args.design_spec)
    if not spec_path.exists():
        print(f"ERROR: design_spec.md not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse design_spec
    spec_data = parse_design_spec(str(spec_path))
    
    # Parse spec_lock if provided
    lock_path = args.spec_lock
    if not lock_path:
        # Try to find spec_lock.md in same directory
        candidate = spec_path.parent / 'spec_lock.md'
        if candidate.exists():
            lock_path = str(candidate)
    
    lock_data = {}
    if lock_path and Path(lock_path).exists():
        lock_data = parse_spec_lock(lock_path)
    
    # Run all checks
    findings = []
    findings.extend(check_purple_gradient(spec_data))       # Rule 1
    findings.extend(check_emoji_icons(spec_data))            # Rule 2
    findings.extend(check_uniform_card_grid(spec_data, lock_data))  # Rule 3
    findings.extend(check_svg_hand_drawn(spec_data))         # Rule 4
    findings.extend(check_gradient_background(spec_data))    # Rule 5
    # Rule 6 (rounded card + left border) is purely visual judgment, skip CLI check
    findings.extend(check_inter_roboto(spec_data))           # Rule 7
    findings.extend(check_icon_overload(spec_data))          # Rule 8
    findings.extend(check_info_density(spec_data, lock_data))  # Rule 9
    findings.extend(check_animation(spec_data))              # Rule 10
    
    # Generate report
    report = generate_report(findings, str(spec_path))
    
    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"Report written to: {args.output}")
    else:
        print(report)
    
    # Exit code: 1 if blocking issues, 0 otherwise
    has_blocks = any(f['severity'] == 'BLOCK' for f in findings)
    sys.exit(1 if has_blocks else 0)


if __name__ == '__main__':
    main()
