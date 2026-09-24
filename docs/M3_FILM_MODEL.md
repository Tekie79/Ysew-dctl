# M3 advanced film model

Version `0.3.0-alpha.1` adds an opt-in **YS Advanced** negative/print model.
The existing `Legacy` model remains the default so earlier saved grades keep their
numerical behavior.

This is an original parametric model. It is **not** a measured Kodak/Fuji stock profile,
not a spectral dye simulation and not a substitute for a calibrated film scan dataset.

## Advanced negative

The advanced negative keeps the existing scene-linear exposure curve, then adds:

- neutral density trim in base-10 density units;
- density-inspired log channel-ratio separation for positive RGB regions;
- graceful reduction of that log-ratio operation around negative wide-gamut components;
- exposure-dependent shadow and highlight chroma retention;
- the existing RGB interaction/crosstalk stage;
- hue-selective warm, green and cyan/blue density biases;
- luminance restoration after hue-dependent color changes.

`Neg Shadow Sat` and `Neg High Sat` are retention multipliers, not absolute
saturation values. The fixed hue families are deliberately broad and overlap softly;
they are artistic response controls, not semantic object masks.

## Advanced print

The advanced print keeps the existing print contrast/toe/shoulder controls and adds:

- independent shadow and highlight density trims;
- neutral print density;
- a second, gentler log-ratio color-separation stage;
- master print color;
- a luminance-preserving warm print bias weighted toward upper midtones/highlights.

The model remains in the working scene-linear pipeline until the existing display render.

## Compatibility

`Film Model = Legacy` is default. Every M3 control is appended after all M2 controls.
M2's first 67 controls and existing Input/menu indices are frozen in
`tests/ui_m2_compat.json`. M3 controls are completely inert in Legacy mode.

## Creative status

The mechanics are implemented, but the numeric defaults are **provisional Yekermo Sew
starting values**. They have not been approved as the final Fall/Winter series look.
Representative footage review is still required before calling a preset show-mastered.

## Acceptance

CPU tests cover legacy inertness, neutral preservation, density scaling, selective
shadow/highlight chroma, hue selectivity, print black/white selectivity, monotonic neutral
ramps, guide parity and randomized finite output. Resolve/Metal visual and performance
acceptance remains a separate gate.
