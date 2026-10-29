# Image to Native PPTX Skill

[简体中文](README.zh-CN.md) · English

Reconstruct approved slide screenshots as **editable Microsoft PowerPoint objects**: text boxes, shapes, lines, freeforms, tables and charts with editable data. Reference images are used for measurement and comparison, never embedded in the resulting deck. Photography can become native placeholders when requested.

This is an **agent-assisted workflow**, not an automatic OCR-to-perfect-slide converter. An agent reads the reference, measures and authors its layout, then renders and reviews the result. It does not claim pixel equality or an uncalibrated 95% similarity.

## Install

Requirements: Node.js 20+, Python 3.10+, and desktop Microsoft PowerPoint for real Office verification. Font files and Office are not bundled.

```sh
git clone https://github.com/2867094562a-code/image-to-native-pptx-skill.git
cd image-to-native-pptx-skill
npm ci --ignore-scripts
python3 -m pip install -r requirements.txt
```

For Codex discovery, clone this repository into `~/.codex/skills/image-to-native-pptx` instead, then restart the app or reload skills. Do not overwrite an existing skill directory. Other agents that understand `SKILL.md` can use the same entry point. Run dependency commands inside the cloned directory.

Example request:

> Use $image-to-native-pptx to reconstruct these approved slide images. Preserve the wording, layout and page order. Use native photo placeholders, no image objects, and provide an Office-verified PPTX plus audit and comparisons.

## Run the included example

```sh
node scripts/build_native.cjs examples/layout.json work/example.pptx
python3 scripts/audit_native_pptx.py work/example.pptx --output work/Native_Audit_Report.json
```

`examples/layout.json` contains a measured two-slide demonstration with native stat blocks, a timeline, progress bars, a placeholder, an authored curve, a table and a chart. Regenerate its JSON recipes with `node scripts/make_example.cjs`.

To create your own reconstruction:

1. Inventory references with `python3 scripts/inventory_images.py references --output work/inventory.json` and record the actual source order.
2. Analyze the images and author measured `layout.json` using the [layout format](references/layout-format.md). Tiny or ambiguous source text must be reviewed rather than invented silently.
3. Build one complex page and render it in PowerPoint. Preserve an approved native sample's construction when one exists, then expand the remaining pages.
4. Audit, verify in desktop Office, export PNGs and compare every page. Iterate by editing native objects.
5. Deliver source, layout data, audit, comparisons and a quality report stating remaining differences.

The JSON renderer exposes **no image API**. It also normalizes repeated paragraph properties, duplicate object IDs and dangling chart-axis references found in generated files. These checks do not replace real Office validation.

## Native component and template reuse

The included `native_components.cjs` has original stat, progress, timeline and photo-placeholder recipes plus three optional palettes. [PptxGenJS](https://github.com/gitbrent/PptxGenJS) supplies native primitives; [pptx-automizer](https://github.com/singerla/pptx-automizer) reuses existing editable component libraries. Both are installed by `npm ci`.

```sh
# Reuse native slides from an existing component library.
node scripts/reuse_native.cjs library.pptx work/reused.pptx 2,7,9

# Split original native parts without rebuilding them (1-based slide numbers).
python3 scripts/split_pptx.py complete.pptx work/template-B.pptx --slides 1-4,13-24
```

The splitter follows package relationships and removes unreachable slides, charts and workbooks. It preserves source order within the requested sequence. Inspect each resulting file in Office. See [library research](references/libraries.md) for alternatives and actual installation/test scope.

## Office verification

On Windows with Microsoft PowerPoint:

```sh
python scripts/office_verify_windows.py work/example.pptx --output work/Office_Final.pptx --renders work/Office_Rendered --report work/Office_Verification.json
python scripts/audit_native_pptx.py work/Office_Final.pptx --output work/Native_Audit_Report.json
```

The helper edits native text, saves to a new file, compares content inventory, closes, reopens and exports each slide. **The Windows COM helper has not been executed on Windows in this project.** macOS verification uses the real PowerPoint app's UI; see the [Office verification guide](references/office-validation.md). LibreOffice previews must be labeled as such.

Comparison images must be named `slide-01.png`, etc.:

```sh
python3 scripts/compare_pages.py work/Reference work/Office_Rendered work/Comparison
```

The audit fails for slide media, picture/blip objects, image/OLE relationships and duplicate native IDs. It reports text coverage against the declared layout inventory and basic bounds/overlap review candidates. It is not independent OCR validation or full schema/visual acceptance; complex groups, rotated objects and font overflow require rendered inspection.

## Tests and limits

```sh
npm test
```

Tests build the native example, verify charts/tables and editable workbooks, confirm image-injection failure, check selected-slide order and exercise native library reuse. No automatic reference-image recognition, photorealistic native reconstruction, guaranteed font matching or similarity certification is provided. Use licensed fonts from official sources; font binaries, user presentations and source screenshots are not distributed here.

Source code is MIT-licensed. Dependencies retain their upstream licenses. This project is not affiliated with Microsoft.
