# Graphical controls and guides - alpha.2

This build provides two native color-picker controls and five optional viewer
guides. It does not provide mouse-draggable curves, wheel handles, a custom OFX
inspector, a waveform, or frame statistics. Drawn guides are read-only visual aids
that respond to the existing sliders. An interactive curve/wheel editor would be
a separate companion-UI implementation, not a misleading name for these overlays.

## Native color pickers

`Range Color` supplies the hue center when `Pick Range Hue` is enabled. `Skin Color`
supplies the hue center when `Pick Skin Hue` is enabled. The manual Range Hue and
Skin Hue remain available; they are the fallback for neutral, out-of-range or
invalid swatches. Only hue is taken from the selected color. Width, feather,
saturation and luminance limits are not silently changed.

The swatches are explicitly interpreted as normalized **display-encoded Rec.709
RGB**, matching the diagnostic hue convention. Use the native color dialog for
the first check. A viewer eyedropper may sample a different processing/encoding
stage: raw/log samples are not automatically decoded or white-balanced. That
sampling behavior still needs host verification; do not assume a log pixel is a
Rec.709 swatch. Skin selection remains a chromatic candidate, not a face detector.

Blackmagic introduced the DCTL color picker and label tooltips in Resolve 19.1
[S4 in SOURCES.md]. Alpha.2 therefore targets 19.1 or later, with the user's 21.1
installation as the immediate acceptance target. It has not yet passed that host
test. The two small probes separate classic controls from color-picker support.

## Visual Guide menu

| Guide | What it draws | Controls to adjust |
|---|---|---|
| Tone Curve | Current neutral-input response, RGB traces and an ungraded neutral reference; input EV on X, encoded output RGB 0..1 on Y | Exposure, balance, negative, print, look and Output Gray |
| Exposure Band | Selected EV interval with feathered 0..1 match weight | EV Min, EV Max, EV Softness, EV Span |
| Color Range | Hue/saturation disk showing selected hue sector and saturation interval, plus a separate luma-range strip | Range Hue or Range Color, Range Width, Range Softness, saturation/luma bounds |
| Skin Range | Hue/saturation disk for the skin-color candidate; no invented fixed skin brightness target | Skin Hue or Skin Color, Skin Width and saturation bounds |
| Vignette | Amber inner boundary, cyan outer feather boundary and white center crosshair | Vig Radius, Vig Softness, Vig Shape, Vig X and Vig Y |

The tone plot evaluates the actual pointwise balance/negative/look/print/output
functions on synthetic neutral DWG inputs. It intentionally excludes the spatial
vignette; it is not a histogram of the clip. The color disks are schematic HSV
selection maps, not calibrated gamut plots or vectorscopes. Their angular hue and
radial saturation selectors are shown separately from the color range's Y-prime
filter. Skin candidates use the fixed neutral preview described in DIAGNOSTICS.md.

Guide Opacity adjusts the drawing. Rectangular panels are omitted below 480x270
to avoid illegible overlays; the warning stripe remains. The vignette guide also
assumes square pixels, like the underlying alpha.1 vignette. Performance of the
extra drawing/curve evaluation on the target GPU has not been measured.

## Output safety

All guides default Off and require internal Rec.709 output in a controlled
terminal path. With guides Off and the picker switches Off, alpha.1 numerical
behavior is retained within tested float32 tolerances. A 64-case regression fixture
and the existing numerical suite verify that condition on CPU, not in Resolve.

Guides modify output pixels when enabled. Disable **Visual Guide** and
**Diagnostics** before delivery. The amber/black stripe is a reminder, not an
interlock. Do not grade or export an additional output conversion after the
internal Rec.709 renderer. Future OFX widgets could avoid rendered overlays, but
that is not the architecture of this build.
