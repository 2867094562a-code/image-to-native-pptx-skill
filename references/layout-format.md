# Executable measured layout

Top level: `width_px`, `height_px`, optional `font`, `lang`, `title`, and ordered `slides`. Each slide has `background` and ordered `objects` (back to front).

Every object has a unique `id`, `type` and `bbox: [x,y,w,h]` in reference pixels. Conversion uses 96 pixels/inch; the canvas aspect ratio is preserved. The format intentionally has no image object.

| Type | Fields |
|---|---|
| `textbox` | `text`, `font`, `font_px`, `color`, `bold`, `align`, `valign`, `wrap` |
| `shape` | `geometry` (PowerPoint preset name), `fill` (hex or `{colors:[hex,hex],angle:0}`), `stroke`, `stroke_px` |
| `freeform` | `commands`, `fill`, `stroke`, `stroke_px` |
| `line` | `color`, `stroke_px`, `arrow`, `flipH`, `flipV`; bbox dimensions must be nonnegative |
| `table` | `values` (rows of strings), optional `col_px`, `font_px`, `header_fill`, `body_fill`, `stroke` |
| `chart` | `chart_type` (`bar`, `line`, `donut`, `radar`), `series`, `colors`, `legend`, `labels`, optional PptxGenJS `options` |

Freeform commands use a local **0–100** viewport, scaled to the bounding box: `M x y`, `L x y`, `Q cx cy x y`, `C c1x c1y c2x c2y x y`, `Z`. These are authored editable DrawingML paths, not SVGs.

Chart series use `[{name:"Current",labels:["A","B"],values:[3.2,4.1]}]`. A native chart workbook is embedded. It is a chart data source, not an OLE substitute.

Additional provenance fields are retained in your source JSON even when the simple builder ignores them: `source_file`, `source_region`, `uncertainty`, `data_provenance`, `photo_placeholder`, `font_substitution`. Keep ambiguous content explicit. For declared text audit, place one page's object inventory in each `slide-01.layout.json`; table cells are included in coverage checks.

See `examples/layout.json` for a working two-page example. More elaborate native text runs, grouping, effects or connectors can be authored directly in PptxGenJS while preserving the same measurements and audit pipeline.
