# Changelog

## 0.3.0-alpha.1 - 2026-09-24

M3 advanced film-response implementation on `develop`.

- Added opt-in `Film Model = YS Advanced`; Legacy remains default.
- Added negative density, master color, log-ratio separation, shadow/highlight chroma retention and warm/green/cool hue-family biases.
- Added print black/white density trims, print separation, warm bias and master color.
- Extended the Tone Curve guide so it evaluates the advanced pipeline.
- Added a frozen 67-control M2 compatibility contract and M3 regression/property tests.
- The model is original and parametric; no measured stock profile or commercial LUT data is claimed or included.
- Final M3 CI passes 107 tests with both Clang and GCC.

## 0.2.0-alpha.1 - 2026-09-24

M2 technical input-science implementation on `develop`.

- Added ARRI LogC4/AWG4, Sony S-Log3/S-Gamut3.Cine, Sony S-Log3/S-Gamut3 and RED Log3G10/REDWideGamutRGB input modes while preserving existing Input indices 0-2.
- Added CAT02 white balance with source CCT, CIE 1960 Duv and strength controls; Legacy remains default and preserves prior Warmth/Tint behavior.
- Added independent published camera reference-vector tests and a distinct `YSEW_Film_Lab_M2.dctl` filename for host testing.
- CI passes 94 tests with both Clang and GCC.
- Resolve/Metal and actual ProRes RAW converter-output acceptance remain pending.

## 0.1.0-alpha.2 - 2026-09-24

Repair quoted/long UI labels and menu text; use plain numeric UI literals; add hover tooltips and strict UI metadata validation. Preserve the first 57 parameter IDs/types/numerical defaults/enum ordering. Add two opt-in hue color pickers and five read-only viewer guides, with display-domain guards and export warnings. Add classic/picker UI probes and an exact A2-named distribution copy.

76 CPU/source tests pass under Clang 17 and GCC 14.2, including 64 alpha.1 regression cases, probe bindings, control-contract checks and actual tone-guide/pipeline comparison. Alpha.1 host control-load failure is recorded; alpha.2 Resolve retest remains pending. No additional film-stock, halation, bloom or grain completion is claimed.

## 0.1.0-alpha.1 - 2026-09-24

Initial M1 implementation on `develop`, branched from the existing `main` commit `479211485d88915edb7e7b892e1c21cb85de97e1`.

Added original color-pipeline DCTL with three scene-input encodings, three output modes, balance/density controls, negative and print curve prototypes, provisional fall/winter looks, candidate-skin protection, vignette, SDR rendering, gamut compression, 26 diagnostic modes, and a numerical scene-exposure legend. Added a reproducible distribution, 43 native-code CPU tests, a stable UI declaration contract, and development/host-validation documentation.

Local Clang 17 and GCC 14.2 CPU tests passed. Resolve DCTL parsing, Metal/CUDA/OpenCL execution, playback, actual footage, monitoring and delivery remain unvalidated. The full spatial/temporal film pipeline is not yet implemented.
