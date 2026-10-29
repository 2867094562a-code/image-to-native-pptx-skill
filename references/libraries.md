# Installable native PowerPoint tooling

Checked 2026-10-29 against upstream repositories. These are programming libraries or add-ins, not a universal gallery of polished native business components.

| Project | Installation / platform | Native workflow fit |
|---|---|---|
| [PptxGenJS](https://github.com/gitbrent/PptxGenJS) | `npm install pptxgenjs`; Node.js, MIT | Native text, shapes, tables and editable charts; generation engine used here. |
| [pptx-automizer](https://github.com/singerla/pptx-automizer) | `npm install pptx-automizer`; Node.js, MIT | Import existing slide/shape libraries, preserve their styles and modify content. Useful for reusing approved components. |
| [@office-kit/pptx](https://github.com/office-kit/pptx) | `npm install @office-kit/pptx`; TypeScript/ESM | Reads/edits/writes decks and supplies a TSX authoring ecosystem. Upstream marks it pre-1.0; pin a version and test fidelity. Evaluated from documentation, not installed here. |
| [PowerPointLabs](https://github.com/PowerPointLabs/PowerPointLabs) | Desktop PowerPoint productivity add-in | An in-Office alternative to inspect if a ribbon-based workflow is desired. Not installed or verified on this Mac. Check upstream platform and Office-version support. |

This repository pins PptxGenJS 4.0.1 and pptx-automizer 0.8.2 in `package-lock.json`. `npm ci --ignore-scripts` installs them. The local smoke test reused table, chart and component slides and then ran the native-only audit. It does not certify every feature of either upstream library.

No upstream source is vendored. Each dependency retains its own license. Supplied component recipes are small original native objects, not a redistributed screenshot or proprietary template collection.
