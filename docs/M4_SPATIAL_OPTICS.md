# M4 spatial optics

Version `0.4.0-alpha.1` moves Film Lab to the texture-sampling DCTL transform so
neighboring pixels can drive optical effects. `Optics` is Off by default.

Pipeline order: balance -> bloom/glow/veiling glare -> negative -> halation -> show
look -> print -> vignette -> output.

The highlight source is scene-linear DWG with thresholds expressed in stops relative
to 18% gray. Each effect samples two rings. Draft uses 4 directions per ring,
Standard 8 and High 16. Radius controls are reference pixels at 2160 image lines and
scale with frame height. Zero effect amount skips that effect's texture sampling.

Contributions use the positive neighborhood-minus-local highlight difference, so a
uniform bright field remains unchanged while bright boundaries can spread into darker
neighbors.

Halation uses a red-to-orange spectral proxy. Bloom retains more source color. Glow
uses a larger radius and partial neutralization. Veiling Glare uses the largest radius
and stronger neutral weighting. These are original finite-radius approximations, not
measured film-base scattering or a calibrated lens PSF.

`Optics View` shows Halation, Bloom, Glow, Veil or their Sum through the internal
Rec.709 inspection path, amplified by Diag Gain. It is a contribution diagnostic, not
a radiometric measurement.

The first 81 M3 controls are frozen in `tests/ui_m3_compat.json`. Resolve/Metal
texture-signature acceptance and performance are deferred to the comprehensive final
test requested for the project.
