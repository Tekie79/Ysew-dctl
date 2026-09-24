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
