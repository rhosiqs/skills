---
name: svg-pptx
description: Convert an SVG (typically one produced by the svg skill) into a .pptx whose every element is a native, editable PowerPoint object (shapes, text boxes, lines, freeforms), never a flattened picture. Defaults to 16:9; if the SVG does not fit 16:9 cleanly, asks the user which handling to use via a popup. Use only when the user invokes /svg-pptx, or explicitly asks to export or convert an SVG, diagram, chart or illustration into a presentation, slides or .pptx (e.g. "export this as a presentation", "turn this diagram into editable slides"). Do not trigger for general requests to create a slide deck.
---

# SVG → editable PPTX

Read `/mnt/skills/public/pptx/SKILL.md` first; its pptxgenjs gotchas apply (hex without `#`, `isTextBox: true`, `margin: 0`, fresh option objects per call, run `validate.py`).

## Rule

Every SVG element becomes a native PPTX object. Never embed the SVG or a rasterized render as a picture. Only `<image>` elements may become pictures.

## Workflow

1. **Get the SVG source** (file, or the markup from the earlier svg-skill output) and save it to a file.
2. **Resolve before converting:** CSS variables (`var(--…)`), `<style>` classes, inherited attributes, `currentColor`, and all `transform`s (flatten translate/scale/rotate/matrix into absolute coordinates). Output colors as 6-digit hex.
3. **Fit check** (see below). If it fails, ask the user; do not guess.
4. **Build** with pptxgenjs, one slide, in document order (z-order = SVG order).
5. **QA:** `validate.py`, render with `soffice.py` + `pdftoppm`, compare against the SVG render. Fix overflow, misplaced text, wrong shapes.
6. **Deliver** with `present_files`. Add one line listing anything dropped or approximated.

## Canvas and fit check

- Default: `pres.layout = 'LAYOUT_WIDE'` (13.333" × 7.5", 16:9). Scale = slide width ÷ viewBox width, uniform on both axes.
- Fit passes only if the viewBox ratio is within ±2% of 16:9 **and** no element extends outside the viewBox.
- On failure, call `ask_user_input_v0` (popup) with one question and these options, then stop and wait:
  1. Scale to fit, centered (letterbox, no cropping)
  2. Set slide size to the SVG's own ratio
  3. Crop to 16:9
  4. Stretch to fill 16:9 (distorts)
- Question text states the SVG's ratio and the specific problem (e.g. "The SVG is 4:3; fitting it to 16:9 leaves empty margins or crops content").
- Apply the choice, then continue from step 4.

## Element mapping

| SVG | PPTX |
|---|---|
| `rect` | `RECTANGLE`; with `rx` → `ROUNDED_RECTANGLE` (check radius in render) |
| `circle`, `ellipse` | `ELLIPSE` |
| `line` | `LINE` (`dashType` from `stroke-dasharray`, `endArrowType`/`beginArrowType` from `marker-end`/`marker-start`) |
| `polyline`, `polygon`, `path` | `custGeom` with `points` (`moveTo`, line, `curve` cubic/quadratic, `close`); arcs → convert to cubic beziers. Coordinates are inches relative to the shape's bounding box |
| `text`, `tspan` | `addText` with `isTextBox: true`, `margin: 0`, `wrap: false`; one run per `tspan`; `font-size` px × 0.75 = pt; `text-anchor` → `align`; position by baseline, not top; box width = estimated text width + 10% |
| `image` | `addImage` |
| `g`, `use`, `symbol` | flatten (no grouping); expand `use` |
| `fill`/`stroke` + `*-opacity`, `opacity` | color + `transparency` (0–100) |
| `stroke-width` | px × 0.75 = pt |

## Not convertible

Gradients, filters, masks, clip paths, patterns, blend modes: approximate (gradient → solid color from its middle stop; others dropped) and report. Do not rasterize to compensate.

## Text

Use the SVG's font-family if installed on common systems, else `Arial`; for CJK text use a CJK-capable font such as `Microsoft JhengHei` or `Arial Unicode MS`. Leave ~10% width slack so PowerPoint's rendering does not wrap or clip.
