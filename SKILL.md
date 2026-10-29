---
name: image-to-native-pptx
description: Reconstruct approved slide screenshots as editable PowerPoint text, shapes, tables and charts. Use when visual references already exist and the user needs a native PPTX rebuild, native-only audit, or separate editable template decks.
---

# Image to Native PPTX

Rebuild the supplied visual reference. Preserve its content, page sequence, geometry and visual language. This is an agent-assisted reconstruction workflow, not a one-click screenshot converter.

## Establish the source

Locate readable original files, attachments and accessible session outputs before asking for missing material. Inventory dimensions with `scripts/inventory_images.py`. Record original page order explicitly; directory sort order is only a discovery aid. A contact sheet containing four slides must be divided into four reference regions in the original reading order, not inserted as a slide. Reference crops are analysis artifacts only.

If files are inaccessible, state exactly what was searched. Do not claim to have read an unavailable reference, regenerate the reference, or invent missing copy. Track ambiguous source text and inferred chart values in the layout data.

## Reconstruct native objects

1. Measure the source pixel canvas and object bounds. Record `bbox: [x,y,width,height]` in `layout.json`, alongside text, colors, fonts, source region and uncertainty. Read [references/layout-format.md](references/layout-format.md) for the executable format.
2. Rebuild a representative complex page first. If the user has already approved native samples, use their construction and detail level as the quality baseline. Inspect a rendered result before expanding the deck.
3. Use native TextBox runs for all copy, Shape/Line/Connector for geometry, Table for tables and Chart plus editable workbook for statistical charts. Use authored DrawingML freeforms for complex icons and curves. Prefer concise meaningful paths over thousands of traced bitmap edges.
4. Keep the approved palette, typography, layout, layering and page count. Install a licensed font from its official source when needed, recording substitutions rather than silently changing the typography. Do not distribute a font without checking redistribution terms.
5. Use native photo placeholders only when allowed by the user. Do not attempt to represent photography or texture with a noisy contour mesh. Describe the remaining visual difference.

The supplied `build_native.cjs` creates measured native elements from JSON, including editable freeforms and gradients through `finalize_native.py`. `native_components.cjs` supplies small reusable stat, progress, timeline and placeholder recipes with three example palettes; these palettes are optional demonstrations, never a replacement for an approved reference. `reuse_native.cjs` uses pptx-automizer to reuse existing native library slides. Keep original native objects when a matching PPTX is available.

For a native-only assignment, never insert original screenshots, cropped screenshot mosaics, raster/SVG image objects, hidden reference images, image fills or OLE substitutes. Rendering images are permitted only outside the final PPTX for inspection.

## Validate in the real medium

Run `scripts/audit_native_pptx.py` after generation and again after the final Office save. It reports native counts, media/image/OLE violations, declared text coverage, duplicate object IDs, simple bounds and overlap review candidates. Bounds are a heuristic for axis-aligned objects; complex group transforms, rotated text, font overflow and visual fidelity require rendered inspection. A structural pass does not establish source-text correctness or a similarity score.

On Windows with installed Microsoft PowerPoint, use `office_verify_windows.py` to exercise a native text edit, save to a new file, close, reopen, compare content inventory and export PNGs. Review Office repair warnings; a successful COM call alone does not prove absence of a warning. On macOS, perform the equivalent open/edit/save/close/reopen and PNG export with the available native-app controls. Never label a LibreOffice or web preview as Microsoft Office verification. Report the actual platform and any unperformed checks.

Compare every rendered page with its source, fixing layout differences in native objects. Use `compare_pages.py` for side-by-side review. Do not claim 95% or pixel equality from an uncalibrated metric. Stop automatic retries after three failed attempts at the same Office-open issue and report the concrete error and retained files.

If a generated package contains repeated `a:pPr` in a paragraph, duplicate native IDs or dangling chart axis references, `finalize_native.py` normalizes these known issues. Preserve the original and compare text/object inventories after any Office normalization; never accept silent content loss.

## Delivery

Provide the editable PPTX, generation source, per-page layout data, comparison renders, `Native_Audit_Report.json` and a quality report describing photos/placeholders, font substitutions, ambiguous copy and inferred data. Split independent templates with `split_pptx.py`; it extracts original native parts and prunes unreachable slides without redrawing them. Follow the user's requested scope and retain original page order within each template.

Read [references/office-validation.md](references/office-validation.md) for platform-specific verification and [references/libraries.md](references/libraries.md) when choosing reusable PPT tooling. Installation and usage are documented in [README.md](README.md) and [README.zh-CN.md](README.zh-CN.md).
