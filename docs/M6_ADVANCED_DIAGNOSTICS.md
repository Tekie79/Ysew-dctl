# M6 advanced diagnostics

Version `0.6.0-alpha.1` adds destination-gamut and scene-calibration inspection while
leaving Film Lab's normal output path unchanged.

## Target gamuts

`Diag Gamut` selects:

- Rec.709 / D65
- P3-D65
- Rec.2020 / D65

For diagnostics, the current working-space result is converted through XYZ into the selected
linear target gamut. The same neutral SDR tone curve used by Film Lab's internal preview is
applied to target luminance, but **no target gamut compression is applied before measurement**.

This gives three views:

**Target Gamut** — categorical inside / near / outside status.

**Gamut Occupancy** — chroma excursion from the target neutral axis normalized to the target
RGB cube boundary. Neutral is 0; the chromatic boundary is 1; materially above 1 is outside.

**RGB Headroom** — minimum target-linear distance to any 0 or 1 cube face. Negative values are
outside. `Gamut Margin x1k` controls the near-boundary inspection band.

These diagnostics do not replace a perceptual gamut mapper or qualify a P3/Rec.2020 deliverable.

## Scene calibration

Calibration modes use the existing Source/Balanced measurement tap.

Profiles:

| Profile | Scene-linear luminance target |
|---|---:|
| 18 Gray | 0.180 |
| 90 White | 0.900 |
| 2 Black | 0.020 |
| Custom | `Cal Target x1k / 1000` |

`Cal Exposure` reports stop error relative to the selected luminance target.

`Cal Neutral` converts the measured DWG value to XYZ and calculates Euclidean CIE-xy distance
from D65 (0.3127, 0.3290). This is a simple chromaticity-distance test, **not CIE Delta E**,
not a camera white-balance estimator, and not semantic neutral-object detection.

`Cal Combined` reports the two conditions together.

## Precision policy

Exact standardized primary colors can accumulate very small negative values through chained
32-bit matrix conversions. M6 treats values within 1e-5 of a target cube face as on/near the
boundary rather than falsely out-of-gamut. Larger excursions remain red/outside.

## Output ownership

M6 does not append P3 or Rec.2020 to Film Lab's Output menu. Rec.709 remains the current
internally rendered mastering output; DWG options remain working outputs for an external
renderer. Additional qualified display/output transforms remain M8 work.

## Global-analysis boundary

A single DCTL can color each pixel according to its own state and neighborhood but cannot
truthfully provide persistent reference-frame storage or general frame-reduction products such
as histogram counts, waveform-density buffers, vectorscope-density histograms or 3D point-cloud
statistics. See `M6_SCOPE_COMPANION.md` for the proposed architecture.

## Validation

The final M6 CI run passed 149 tests under both GCC and Clang. Resolve/Metal UI and display
qualification remain deferred to the comprehensive final test.
