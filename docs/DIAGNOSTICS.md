# Diagnostic reference

## Measurement rules

A diagnostic must state what it measures and where. In M1, scene exposure is `log2(Y/reference_gray)` in decoded scene-linear DWG. The default gray is 0.18. It is relative image exposure, not a recovered camera exposure, incident-light meter, sensor clipping level, dynamic-range measurement or assessment of recoverable detail. The quantity is only meaningful when the input encoding and upstream scene normalization are correct. Source clipping/noise calibration would need independent camera/decoder evidence.

The source/balance selector affects scene-derived modes only. Output modes are fixed to the internal Rec.709 renderer. The color-range selector measures **encoded Rec.709 HSV hue and saturation plus Y-prime**, not an unspecified 'true color', perceptual chroma or CIE Delta E. Individual RGB stop views measure components of the chosen working basis, not sensor photosites.

**Diagnostics require internal Rec.709 output in an unmanaged terminal node path.** Selecting working-space output with a diagnostic enabled produces a warning checkerboard instead of silently emitting mis-encoded measurement colors. An external RCM/ACES/CST/output LUT can alter diagnostic colors and is not discoverable by this shader; the DCTL cannot automatically disable it.

Every diagnostic has an amber/black top stripe, even when its legend is disabled. This is a visible safety indicator, not an export interlock. Set diagnostics to Off before rendering delivery.

## Modes

| ID | Mode | Measurement and display |
|---|---|---|
| 0 | Off | Normal selected pipeline output. |
| 1 | Scene false color | Relative scene Y stops; continuous, whole, half or third-stop coloring. Scale endpoints are display bounds, not clipping labels. |
| 2 | Scene exposure grayscale | Relative scene Y stops mapped to a symmetric grayscale scale. Zero stops is 0.5. It is not a normal black-and-white grade. |
| 3 | Scene zones grayscale | One-stop digital zones; middle gray at Zone V, zero-to-ten zone display bounds. Not a film-specific print-zone calibration. |
| 4 | Scene exposure range matte | Inclusive low/high EV band with optional feather. Nonpositive Y is excluded. |
| 5 | Scene exposure range overlay | The same range over the finished preview, with adjustable opacity. |
| 6 | Scene RGB relative stops | Independent DWG components relative to the reference; nonpositive components map to the lower display bound. |
| 7 | Output grayscale Y-prime | Weighted encoded R-prime/G-prime/B-prime. |
| 8 | Output luma false color | 0..1 encoded Y-prime mapped across the heat palette; not source exposure. |
| 9 | Output linear luminance viewed | Decode output Gamma 2.4, calculate linear Y, then encode that scalar for viewing. |
| 10 | Output hue map | Encoded Rec.709 HSV hue shown at full chroma. Achromatic pixels are gray because hue is undefined. |
| 11 | Output HSV saturation heat | `(max-min)/max` in encoded RGB. Not perceptual saturation. |
| 12 | Output RGB chroma heat | `max-min` in encoded RGB. Not CIE chroma. |
| 13 | Color range matte | Circular hue range, HSV saturation interval and Y-prime interval. |
| 14 | Color range isolate | Selected colors over a dim grayscale background. |
| 15 | Candidate skin matte | Chromatic candidates from a fixed neutral view of the selected scene tap; not semantic detection. |
| 16 | Candidate skin relative exposure | Source/balanced scene stops under the same candidate mask. No universal skin-brightness target. |
| 17 | Neutral candidate chromatic bias | Amplified RGB differences from Y-prime for low-saturation candidates. Not a determination of correct white balance. |
| 18 | Scene nonpositive RGB channels | R/G/B flags for components at or below zero. Negative wide-gamut values can be valid; this is not a sensor-crush alarm. |
| 19 | Pre-gamut channel limits | Channel flags at or above 0.995 in the rendered, uncompressed linear Rec.709 cube. Negative components below -1e-6 get a checkerboard. Threshold proximity is not proof of original clipping. |
| 20 | Rec.709 chromaticity warning | Negative target-primary components relative to positive Y indicate outside-triangle colors. Bright neutral values are not treated as chromaticity failures. |
| 21 | SDR RGB volume warning | Linear rendered RGB outside 0..1, distinct from chromaticity-only coverage. |
| 22 | Gamut compression amount | `1-factor` of the actual neutral-axis chroma compression. Zero with compression disabled; does not describe a subsequent hard clamp. |
| 23 | Balanced/finished split | Balanced baseline versus the finished grade, both through the same output renderer. Same frame only. |
| 24 | Display difference amplified | Absolute per-channel encoded RGB difference against that balanced baseline, times Gain. Not perceptual Delta E. |
| 25 | Inspect pipeline stage | Source, balance, negative, look, print, vignette, pre-gamut or final. Working stages receive the same viewing transform; they are not raw numeric stage outputs. Pre-gamut view is clipped for viewing; use modes 19-21 to inspect excursions. |
| 26 | Nonfinite or unsafe input | Black for accepted input; a magenta/dark checkerboard for invalid or numerically unsafe input. The safety checker is active in all modes. |

## Scales and selection

The scene scale spans +/-2 through +/-12 stops. Its bottom legend uses one-stop reference swatches with integer labels; quantization still applies to the image at the selected whole/half/third-stop interval. Half-stop rounding ties go toward the higher stop. The grayscale/zone/range legend uses the corresponding mapping. The RGB-component legend is a neutral reference only. Tiny viewers under 320x160 omit the bottom scale. Output heat maps currently use the documented 0..1 palette without a numeric on-image legend.

The heat palette progresses from dark blue through cyan, green at its midpoint, yellow, then red. These colors indicate position within the chosen scale, not good/bad exposure. Nonpositive scene luminance is black in exposure views. Green at zero stops does not designate a universal skin exposure. Digital-zone views clamp below Zone 0 and above Zone X for display only.

Range low/high values are sorted internally so crossing sliders cannot create undefined intervals. Hue wraps through 0/360 degrees. A half-width of 180 selects the full hue circle. For narrower hue ranges, achromatic pixels are excluded rather than being assigned a fake red hue. Color-range hue feather is adjustable; its saturation/Y-prime feather is currently fixed at 0.02.

For mode 20, green is inside, yellow is near a target-primary boundary (minimum component/Y below 0.02), red is outside, and nonpositive/negligible Y is gray. For mode 21, red is outside the rendered cube, yellow is within 0.01 of a cube face, green is farther inside. Near-black neutral pixels can therefore be yellow in the volume mode without indicating a fault.

## Skin protection relationship

To preview the actual candidate mask used by the show-look protection, set the scene tap to **After balance pre look**. The source tap intentionally shows a different, pre-balance candidate mask. Skin controls set a chromatic candidate, not an ethnicity category or facial identity. There is no fixed luminance window, but camera noise, lighting, encoding and near-zero numerical precision can still affect selection. Inspect it manually; similarly colored objects can qualify.

## Not yet available

Spatial skin-uniformity measurement, distributions/histograms, a true waveform/parade/vectorscope, scene noise-floor estimation, reference-frame comparisons, persistent shot-match statistics, floating-point pixel readouts, arbitrary 3D gamut clouds, camera-calibrated clipping thresholds and automatic export checks require additional implementation and/or a companion host architecture. Do not infer these capabilities from the number of visualization modes.
