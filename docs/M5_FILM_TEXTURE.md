# M5 film texture

Version `0.5.0-alpha.1` adds film texture while preserving the complete M4 path when
`Texture = Off`.

## Pipeline placement

```text
input / camera decode
 -> balance / CAT02
 -> Lens Soft + Micro Soft
 -> M4 bloom / glow / veil
 -> negative
 -> M4 halation
 -> show look
 -> print
 -> density-style grain
 -> vignette
 -> display output
```

Lens softness is placed before the negative because it represents acquisition-style optical
softening. Grain is placed after print because this implementation treats it as final
photochemical texture before display rendering. These are deliberate creative pipeline choices,
not claims that every physical film chain has the same ordering.

## Grain

Grain is generated from smooth value-noise cells driven by DCTL `RAND(uint)`. Each pixel's
seed combines spatial cell coordinates, the user Grain Seed, a channel/layer salt and a temporal
phase derived from `TIMELINE_FRAME_INDEX`.

**Grain Motion**

- Static: frame phase is always zero.
- Every Frame: phase equals timeline frame index.
- Hold 2: phase changes every two timeline frames.
- Hold 3: phase changes every three timeline frames.

The same frame, controls and seed should therefore produce the same grain. Resolve seek/cache/
render behavior will be verified in the final host test.

**Multilayer texture**

A shared field supplies correlated luminance-like grain. Grain Color blends toward separate
R/G/B fields with distinct seeds and slightly different scales. Grain Rough blends single-scale
value noise toward a three-scale mixture.

**Density application**

The grain field is not added to display RGB. Instead each printed working-space channel is
multiplied by `10^(-density_noise)`. Grain Percent controls the density amplitude. Shadow,
Mid and High percentages weight that amplitude from scene/print exposure.

## Gauge and resolution

8mm, 16mm, 35mm and 65mm are **artistic spatial-size presets**. They are not measured stock
profiles, actual silver-halide particle sizes, or claims about a particular manufacturer.
Grain Size x100 multiplies the selected preset.

Coordinates scale against image height with a 2160-line reference, so the grain's normalized
size is intended to remain approximately consistent between delivery resolutions. Very small
output resolutions can naturally alias sub-pixel grain; that will be checked in Resolve.

## Lens and micro softness

Lens Soft uses a weighted center/axial/diagonal neighborhood in balanced scene-linear DWG.
Lens Radius is referenced to 2160 image lines.

Micro Soft uses the same local average only to move luminance toward the neighborhood value,
retaining more of the original chromatic relationship. It is a high-frequency/microcontrast
reduction control rather than sharpening or denoising.

## Diagnostics

Texture View requires internal Rec.709 output:

- Grain: signed, 0.5-centered grain signal.
- Weight: exposure-dependent grain strength.
- Lens: absolute lens/micro-soft contribution.
- Combined: absolute grain plus lens contribution.

The amber diagnostic stripe remains a warning only. Texture View must be Off for delivery.

## Validation boundary

Automated CI passed 134 tests under GCC and Clang. The CPU shim emulates texture reads and
provides a deterministic RAND implementation, but does not reproduce Resolve's private random
sequence or Metal execution. Comprehensive final testing must cover Resolve Studio 21.1,
timeline seeks, cache invalidation, render/re-render consistency, project reopening, actual
frame rates/resolutions, GPU performance and creative approval on Yekermo Sew footage.
