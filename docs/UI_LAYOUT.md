# Yekermo Sew Film Lab — Studio inspector layout

Version: `0.7.0-alpha.3`

Resolve DCTL provides parameter widgets but not native group boxes, tabs or collapsible inspector
sections. Film Lab therefore uses a deliberate workflow order instead of fake header controls.

## Layout

1. **Input** — Input
2. **Balance / White Balance** — Exposure, WB Method/Temp/Duv/Strength, Warmth, Tint, Density RGB
3. **Negative** — Negative enable, Film Model, legacy and advanced negative controls
4. **Show Look / Skin** — Show Look, Look Mix, skin protection, Skin Color picker and skin range
5. **Print** — Print enable, base print response and advanced print controls
6. **Optics** — Optics enable/quality/mix, Halation, Bloom, Glow, Veiling Glare, Optics View
7. **Texture / Grain** — Texture enable, grain controls, temporal motion/seed, Lens/Micro Soft, Texture View
8. **Vignette** — amount, radius, softness, shape and center
9. **Diagnostics / Calibration / QC** — diagnostics, exposure/range controls, Range Color picker, target gamut, calibration, QC, guides
10. **Output** — Output Gray, Gamut Map, Gamut Knee, Output

`Input` is intentionally the first control. `Output` is intentionally the final control.

## Freeze policy

Alpha.3 deliberately changes declaration order before Film Lab has a successful Resolve host
acceptance. After alpha.3, this Studio order is frozen for saved-grade stability. A later major
inspector redesign must use a new version/migration rather than silently reshuffle the existing
parameter declarations.
