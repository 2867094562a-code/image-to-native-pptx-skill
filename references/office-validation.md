# Office acceptance

## Windows

Install desktop Microsoft PowerPoint and `pip install -r requirements.txt`. Run:

```sh
python scripts/office_verify_windows.py work/example.pptx --output work/Office_Final.pptx --renders work/Office_Rendered --report work/Office_Verification.json
python scripts/audit_native_pptx.py work/Office_Final.pptx --output work/Native_Audit_Report.json
```

The COM helper opens a new PowerPoint instance, edits one top-level native text range with identical content, saves to a new PPTX, compares native text/shape/table/chart inventories, closes, reopens and exports every slide. A document without a top-level text range reports `text_edit_test: false`; exercise a grouped text manually in that case. Inspect repair warnings rather than assuming COM success proves clean opening. Do not kill a user's existing Office process to resolve a hang.

The Windows helper is provided but was **not executed on Windows** during development. Development used Microsoft PowerPoint for Mac for open/edit/save/reopen and PNG export, and native OOXML audits. Its platform guard exits explicitly elsewhere.

## macOS

Use the available native-app automation controls. Open the candidate in Microsoft PowerPoint, inspect it for a repair warning, edit an existing native text box, save, close and reopen. Export each slide to PNG using File → Export → PNG → Save every slide. The output is a folder of PNGs. Record actual application/version and completed checks in the quality report. No pywin32/COM claim applies on Mac.

## Structural vs visual checks

A native audit checks pictures, image relationships/fills, OLE objects, native object counts, repeated IDs, declared text coverage and basic bounds. It is not an independent OCR verifier or a complete Open XML schema validator. Group transforms, chart data semantics, font overflow, designed overlaps and rotation need visual inspection. Template splitting preserves native parts, but every resulting file must still be opened in Office.

Screenshots and comparison sheets stay outside the PPTX. Never insert them to improve a comparison result. Photography is explicitly replaced with editable placeholders only when the task permits it. Similarity scores, if used, need a documented method and cannot certify semantic correctness.
