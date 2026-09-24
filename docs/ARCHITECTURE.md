# Architecture and color contracts

## M1 execution

```text
Declared scene RGB input
  -> decode transfer and convert gamut -> scene-linear DWG
  -> exposure / relative RGB balance / density-point trims
  -> parametric negative response
  -> provisional Yekermo Sew look / candidate-skin protection
  -> parametric print response
  -> spatially varying vignette gain
  -> either DWG working output for an external renderer
     or internal SDR rendering -> linear Rec.709 volume compression -> Gamma 2.4
```

The optional diagnostic branch reads stored stages of this same pixel execution. Source exposure is sampled after input decoding but before the grade; balanced exposure is sampled before the negative/look/print. Neither includes downstream nodes outside this DCTL. There is no hidden reference-frame store, global image reduction, AI detector or camera metadata reader.

## Mathematical contracts

**Input.** DWG/Intermediate uses Blackmagic's published piecewise transfer and XYZ matrices [S1]. The negative linear branch is retained. Linear Rec.709 means scene-linear RGB expressed in those primaries, not a gamma-encoded finished Rec.709 image. There is deliberately no ambiguous generic Log, RAW, or display-Rec.709 input in M1.

**Luminance.** DWG scene Y uses the Y row of its RGB-to-XYZ matrix, including the negative blue coefficient. It must not use Rec.709 weights on DWG RGB. Display-linear Rec.709 Y uses the primaries-derived XYZ row; encoded Rec.709 Y-prime uses 0.2126/0.7152/0.0722. These are different measurements [S1, S2].

**Balance.** Exposure multiplies linear RGB by `2^stops`. Warm/cool and tint are relative channel-gain adjustments, not calibrated Kelvin or chromatic adaptation. One density point is an explicitly chosen `0.025 log10` density increment: positive values attenuate the selected channel by `10^(-0.025 * points)`. This is a documented mathematical convention, not a claim of calibrated laboratory printer-light behavior.

**Negative and print.** The current response is an original monotonic log-exposure curve, anchored at 0.18. Softplus-based toe/shoulder terms alter the slope without an artificial nonzero black floor. Saturation operates about scene Y. The negative's RGB interaction is a density-dependent proxy with neutral/luminance protection. The print adds independent contrast/softness/saturation and neutral-density attenuation. Neither stage models spectral dye absorption, measured stock sensitometry or a scanned negative. Identity bypasses are tested.

**Show look.** Fall and Winter are conservative provisional RGB/saturation treatments. Skin protection reduces only the show-look contribution under an editable chromatic candidate mask. It does not exempt those pixels from balance, negative, print, vignette or display rendering. The mask uses a fixed neutral preview of balanced scene RGB, so creative look changes do not chase their own mask. Similar-colored walls/wood can be selected.

**Vignette.** An original normalized, movable, feathered image-space gain. Radius is relative to the frame; roundness interpolates between a frame-fitted ellipse and a circle in pixel geometry. It is not a calibrated lens falloff measurement and does not account for pixel aspect ratios other than 1:1.

**SDR rendering.** For positive scene luminance `Y`, the original rendering curve is `T(Y)=Y/(Y+k)`, where `k=0.18*(1-g)/g` and `g=gray_code^2.4`. Neutral 0.18 therefore reaches the selected encoded gray with the creative stages bypassed. It is not a Resolve DRT replica, ACES transform, camera BT.709 OETF, universal 18%-gray standard or complete display-calibration model. The parameter defaults to 0.42 as a design choice. Print density and other creative operations can intentionally change the resulting gray.

**Gamut mapping.** Transform to linear Rec.709, render luminance, then compress chroma toward a neutral of the same Y. A soft knee limits RGB excursions into the SDR cube. This preserves that linear RGB luminance, not necessarily perceptual hue. Compression disabled uses the final hard clamp instead. Output gamma is a pure 1/2.4 encoding with ideal black; it is not the full nonzero-black BT.1886 display model [S3]. No video-level scaling is baked into pixels.

**Limits.** Nonfinite or absolute raw/decoded component magnitudes above 1e6 produce a visible checkerboard instead of a plausible image. That numeric-safety boundary is not sensor clipping. Creative working output remains signed and unbounded within normal floating-point limits. The final SDR path clamps to 0..1. It cannot reconstruct lost raw channels, infer sensor noise floor, identify actual neutral surfaces, certify broadcast levels, or manage export metadata.

## Planned full-film implementation

The production architecture remains modular. Prototype lens bloom/diffusion and film halation at explicit scene-linear/exposure-domain points; prototype grain in a defined negative/print density domain. Separate lens diffusion from emulsion/base halation. Do not approximate large-radius neighborhoods by simply recoloring highlights. Multi-pass spatial processing may require several DCTL nodes or an OFX companion rather than recomputing the entire grade for every sample.

Changing stage order or the underlying show response can alter every saved grade. Version those changes and retain regression references. A display output owner remains singular in every configuration.

References [S1]-[S4] are listed in [SOURCES.md](SOURCES.md).

## M2 input boundary

M2 expands the declared input boundary with four camera-log choices. Each transfer function is
decoded to relative scene linear, converted from its documented D65 camera gamut through XYZ,
then into scene-linear DWG. No camera mode reads clip metadata or guesses a camera. ARRI LogC4
uses the EI-independent software curve from the current ARRI specification; Sony uses the
published S-Log3 reflection formula; RED uses the published Log3G10 equation.

The optional CAT02 white-balance stage is applied after input normalization and before the
negative/look/print stages. Legacy is still the default and is covered by the alpha regression
fixture. CAT02 maps a user-declared source illuminant to D65; it does not estimate illumination
from the image or reverse white balance already applied by a RAW decoder.

## M3 advanced film model

M3 is selected with `Film Model = YS Advanced`. The negative first applies the existing
log-exposure characteristic curve and neutral density. Positive RGB regions can then receive
log channel-ratio separation; that operation fades toward the original signal around negative
wide-gamut components instead of taking invalid logarithms. Exposure-dependent chroma retention
acts separately in deep shadows and highlights. Broad hue-family density biases are calculated
from a fixed neutral viewing transform and are renormalized to preserve scene Y.

The advanced print applies its characteristic response, region-weighted black/white trims,
neutral print density, a gentler separation stage, master chroma and an optional warm bias.
The print is still not a measured stock or spectral print model. Output ownership and the
existing Rec.709 render remain unchanged.

## M5 film-texture stage

M5 adds two distinct operations. Lens Soft and Micro Soft operate on balanced scene-linear
DWG before the M4 acquisition-optics stage and before the negative. Lens Soft blends toward a
small weighted neighborhood RGB average; Micro Soft shifts local luminance toward the same
neighborhood average while retaining more chroma.

Film grain is applied after the print response and before vignette/output. It is multiplicative:
a deterministic noise value perturbs each print RGB channel by a small base-10 density factor.
This avoids treating grain as a simple display-code additive overlay. Exposure weighting has
independent shadow, midtone and highlight multipliers.

Spatial grain is value noise with optional three-scale roughness. Grain Color blends a shared
noise field toward independent R/G/B fields with slightly different layer scales. Gauge choices
change the base spatial scale and Grain Size x100 multiplies it. The gauge names are artistic
scale presets; no measured 8/16/35/65mm stock scan has been used.

Temporal phase is derived from `TIMELINE_FRAME_INDEX`; samples come from DCTL `RAND(uint)`.
Static ignores frame index, Every Frame changes every frame, and Hold 2/Hold 3 quantize the
timeline frame index. The seed remains user-controlled. Resolution scaling is normalized to a
2160-line reference.

Texture View is a terminal Rec.709 diagnostic. Grain shows a signed 0.5-centered signal,
Weight shows the exposure multiplier, Lens shows the absolute softness contribution, and
Combined shows absolute grain/lens changes.

## M6 diagnostics and analysis boundary

M6 adds target-space diagnostics without changing normal output. A working-space pixel is
converted through XYZ to Rec.709, P3-D65 or Rec.2020, then passed through the same neutral
tone-rendering curve used by the internal SDR preview. The diagnostic intentionally inspects
the **uncompressed target RGB cube** so out-of-gamut status remains visible before a gamut
mapper could hide it.

`Target Gamut` reports outside / near-boundary / inside. `Gamut Occupancy` measures the
current chroma excursion from the neutral axis relative to the available target-cube boundary:
0 is neutral, 1 is the chromatic boundary, and values above 1 are outside. `RGB Headroom`
uses the minimum distance to any 0/1 target RGB cube face. A small 1e-5 numerical tolerance
prevents matrix round-trip noise at exact standardized primaries from being reported as
physically outside.

Scene calibration is measurement-only. The Source/Balanced diagnostic tap is compared with
0.18, 0.90, 0.02 or a user custom scene-linear luminance target. Exposure error is reported
in stops. Neutrality uses Euclidean distance in CIE xy from D65 (0.3127, 0.3290); this is
**not Delta E**, not a white-balance estimator, and does not identify whether an object should
actually be neutral.

A DCTL transform has no persistent reference-frame store and no general frame-reduction output.
Therefore waveform density, histogram counts, vectorscope density, 3D point clouds, percentile
statistics and reference-frame matching belong in the proposed OFX companion rather than being
represented by misleading per-pixel approximations.
