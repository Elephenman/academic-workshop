# Changelog

## v0.4.0 (2026-05-05) — Unified Bugfix Release

### Fixed — Systemic (RED)

- **RED-01**: Created `scripts/win_compat.py` — auto-fixes `sys.path` for C-extension DLLs on Chinese-path Windows. All 24 top-level scripts now import it.
- **RED-02**: Added "Windows执行规范" section to SKILL.md — standardized `Start-Process + 重定向` for all Python script execution on Windows.
- **RED-03**: `win_compat.py` auto-reconfigures `sys.stdout/stderr` to UTF-8 on Windows. Emoji in `print()` now safe.

### Fixed — Functional (YELLOW)

- **YELLOW-01**: `pptx_cli.py` now auto-disables PNG compat mode on Windows (svglib CJK font issue). Added `--force-compat` override flag.
- **YELLOW-02**: (Already resolved in v0.3.1 via C3 native DrawingML route.)
- **YELLOW-05**: `svg_quality_checker.py` now checks spec_lock.md page count against actual SVG file count. Warns on mismatch.
- **YELLOW-06**: `total_md_split.py` now auto-replaces `{{DATE}}`/`{{DATE_CN}}`/`{{DATE_EN}}` placeholders with current date. SKILL.md Step 7 documents this feature.
- **YELLOW-07**: `taste_guardian_cli.py` now has "academic exception" handling:
  - Rule 3 (uniform card grid): BLOCK → WARN when anchor pages exist
  - Rule 9 (info density): message notes dense pages are expected in academic talks
  - Rule 10 (animation): "transition" keyword no longer flagged; message notes fade page transitions are expected

### Improved — Experience (GREEN)

- **GREEN-01**: SKILL.md Step 1 now documents auto-detection of input file type by extension.
- **YELLOW-04**: SKILL.md Step 1.3 now documents paper-deep-read-v3 Figure caption naming tip.

### Files Changed

| File | Change |
|------|--------|
| `scripts/win_compat.py` | NEW — Windows path + encoding compat shim |
| `scripts/*.py` (24 files) | Added `import win_compat` at entry point |
| `scripts/svg_to_pptx/pptx_cli.py` | Windows PNG compat auto-disable + `--force-compat` flag |
| `scripts/svg_quality_checker.py` | Added `_check_spec_lock_page_count()` method |
| `scripts/taste_guardian_cli.py` | Academic exception for Rules 3/9/10 |
| `scripts/total_md_split.py` | `{{DATE}}` placeholder auto-replacement |
| `SKILL.md` | Windows执行规范 section + Step 1 auto-detect + Step 7 date placeholders + Step 1.3 image naming tip |

---

## v0.3.1 (2026-05-05) — Audit Cleanup

### Fixed

- **SKILL.md title**: "9步流水线" → "8步流水线" (actual step count)
- **SKILL.md Step 1**: Added Excel/XLSX input type (matching implementation spec)
- **group-meeting-pipeline**: C3 input description clarified — "C3可独立运行，B1骨架+B3批判为可选增强"
- **group-meeting-pipeline**: Data flow diagram updated — added B1+B3→C3 optional enhancement arrow
- **Test residuals cleaned**: deleted `templates/zju_blue/` (root-level duplicate, formal copy at `templates/layouts/zju_blue/`)
- **__pycache__ cleaned**: removed 3 cache directories (scripts/, image_backends/, image_sources/)
- **Debug scripts removed**: deleted 6 temporary scripts (p1_17_verify, p1_17b_verify, p2_04_verify, theme_debug, theme_ns_debug, theme_quick_test)

### Audit Summary

- File completeness: ★★★★☆ (core files complete, test residuals cleaned)
- Logic consistency: ★★★★★ (8-step pipeline self-consistent after title fix)
- Ecosystem integration: ★★★★★ (group-meeting-pipeline C3 route confirmed)
- Overall: ★★★★★ (4.2→4.8 after cleanup)

---

## v0.3.0 (2026-05-04) — Phase 3: Ecosystem Completion

### New

- **group-meeting-pipeline integration**: C3 学术工坊 added as default recommended PPT engine
  - Updated group-meeting-pipeline SKILL.md: C3 (academic-workshop) as ⭐recommended option
  - Three-engine decision table: C3(academic-workshop) / C1(pptx) / C2(web)
  - C3 auto-includes Phase 4-5 (speech + Q&A), no need to run separately

- **regression-test-plan.md**: Full regression test design for 3 paper types
  - T1: bioinformatics method paper (flow diagrams + heatmaps)
  - T2: experimental results paper (large Figures + breathing pages)
  - T3: review paper (text-heavy + forced breathing pages)
  - Manual + automated verification checklist

- **ppt-master version sync mechanism**: Enhanced asset_map with sync strategy
  - Recorded v2.5.0 source version and 17 ⭐non-overwrite files
  - Manual sync flow + sync history tracking table
  - Clear separation between inherited (syncable) and custom (non-overwrite) assets

### Verified

- **image_gen.py**: --help + --list-backends pass, 15 backends listed (5 CORE/3 EXTENDED/7 EXPERIMENTAL)
- **image_search.py**: --help pass, wikimedia search tested successfully (Deinococcus radiodurans → 165KB JPG downloaded)
- **group-meeting-pipeline**: SKILL.md updated with C3 route, decision table, and checkpoint updated

### Pending (requires real paper input)

- P2-05: paper-deep-read-v3 integration E2E test
- P2-06: qa-defense-system integration E2E test
- P3-05: Full 3-paper regression test (actual execution)

---

## v0.2.0 (2026-05-04) — Phase 2: Taste Enhancement

### New

- **taste_guardian_cli.py**: Machine-assisted anti-AI-slop detection CLI
  - Purple gradient detection (HSL hue 240-300, saturation>50%)
  - Inter/Roboto font detection
  - Breathing page existence check
  - Emoji icon strategy detection
  - Gradient background detection
  - Animation keyword detection
  - Outputs Markdown taste report with BLOCK/WARN/PASS verdict

- **zju_blue template**: Zhejiang University branded template
  - 5 SVG pages (cover/toc/chapter/content/ending)
  - Design spec with dissected theme data (13 theme colors, 2 theme fonts)
  - Primary color #003F88, accent #ED7D31, fonts 思源黑体 CN/CN Light
  - Added to layouts_index.json

- **executor-academic.md**: Enhanced with 5 detailed SVG layout templates
  - Cover: centered title + author info + 40%+ whitespace
  - Method: horizontal step bar + vertical flow chart templates
  - Results: big figure (60-80% canvas) + one insight (2 layout variants)
  - Discussion: dual-column list + comparison table templates
  - Summary: 1-3 bold conclusions + future direction + 50%+ whitespace

### Verified

- All 5 huashu Design distilled files integrated and accessible
- Taste guardian CLI tested against ZJU blue (clean pass) and intentionally bad design (7 BLOCK + 2 WARN detected)
- 19-point integration verification all pass

---

## v0.1.0 (2026-05-04) — Phase 1: Skeleton Build

### New

- 9-step academic PPT pipeline (Input → Init → Template Dissection → 8-Confirm → Taste Guardian → SVG Generation → Speech+Q&A → PPTX Export)
- template_dissector.py v2: deep theme color/font extraction from PPTX
  - Resolves python-pptx theme Part without `.element` via `etree.fromstring(blob)`
  - Handles nested clrScheme with `.findall()` + XPath
  - Maps schemeClr aliases (bg1→lt1, tx1→dk1)
  - Handles GroupShape without `.fill` attribute
  - Resolves theme font placeholders (+mj-ea, +mn-ea) to actual typeface names
- 22 inherited scripts from ppt-master (0 modification)
- 21 layout templates + 70 chart templates + 11631 SVG icons
- 5 huashu Design distilled reference files
- 7 custom reference files (strategist/executor-base/executor-academic/taste_guardian/qa_defense/design_spec_reference/spec_lock_reference)
- ZJU blue template dissected: 13 theme colors, 2 theme fonts, 7 JSON outputs
- Full SKILL.md with 8 iron rules and 9-step pipeline definition

### Known Issues

- Python stdout invisible in PowerShell (workaround: write to file)
- pymupdf import fails with Chinese paths (workaround: sys.path.insert)
