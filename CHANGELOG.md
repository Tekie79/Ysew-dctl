# Changelog

## 0.7.0-alpha.4 - 2026-09-25

Resolve 21.1 Metal frame-key compatibility.

- Resolve alpha.3 reached Metal compilation, proving the texture entry signature repair worked.
- Added a compile-time fallback when `TIMELINE_FRAME_INDEX` is not exposed by the Metal texture-DCTL path.
- Preserved temporal grain on hosts/backends where the documented frame key is exposed; fallback is deterministic/static.
- Added `YSEW_Timeline_Frame_Probe.dctl` to test the documented frame key independently in a pointwise ResolveFX DCTL.
- Renamed the first Balance control to `BAL Exposure` so the section start is visible in the inspector.
- Input remains first and Output remains last.

## 0.7.0-alpha.3 - 2026-09-25

Studio inspector layout and host-signature hardening.

- Reordered all 122 controls into workflow categories.
- Input is now the first control and Output is the final control.
- Group order: Balance/WB, Negative, Show Look/Skin, Print, Optics, Texture/Grain, Vignette, Diagnostics/Calibration/QC, Output.
- Moved Skin Color beside skin controls and Range Color beside diagnostic range controls.
- Preserved all control IDs, types, defaults and combo enum ordering; only declaration order changed.
- Updated compatibility tests to resolve controls by stable ID for this intentional pre-release reorder.
- Added a strict Studio-layout regression test.
- Updated pointwise UI probes to Blackmagic's documented Transform signature formatting.
- Bumped the host-test alias to `YSEW_Film_Lab_M7_A3.dctl`.
- Alpha.3 CI passes 171 tests under both GCC and Clang; deterministic package hash matches across both jobs.

## 0.7.0-alpha.2 - 2026-09-25

Resolve-host entry-signature repair.

- Replaced the M7 texture transform declaration with Blackmagic's documented signature verbatim on one line, including parameter names and spacing.
- Added strict build lint that rejects any deviation from that texture entry signature.
- Added a minimal `YSEW_Texture_Probe.dctl` using the same documented signature.
- No film/color/diagnostic/optics/grain math changed.

## 0.7.0-alpha.1 - 2026-09-24

M7 show-consistency and Rec.709 mastering implementation on `develop`.

- Appended Night, Exterior Day and Exterior Dusk look modes without renumbering existing looks.
- Added QC Pre Gamut, QC Final Range and QC Master diagnostics with configurable boundary/compression thresholds.
- Added five candidate whole-pipeline show profiles, all explicitly pending director review.
- Added versioned shot metrics, reference/candidate comparison and episode batch consistency workflow.
- Added provisional, versioned episode consistency tolerances.
- Added deterministic release ZIP packaging with SHA-256 manifest and production-ready=false safety metadata.
- Added comprehensive Resolve/Metal, creative and Rec.709 delivery-QC checklist.
- M8 remains optional future output/HDR work; M7 does not claim HDR or additional qualified display masters.
- Final M7 CI passes 166 tests with both Clang and GCC; deterministic package hash is identical across both jobs.

## 0.6.0-alpha.1 - 2026-09-24

M6 advanced-diagnostics implementation on `develop`.

- Appended Target Gamut, Gamut Occupancy, RGB Headroom, Cal Exposure, Cal Neutral and Cal Combined diagnostic modes.
- Added diagnostic Rec.709, P3-D65 and Rec.2020 destination targets without changing normal output.
- Added 18% gray, 90% white, 2% black and Custom scene-calibration profiles.
- Added configurable gamut margin, exposure tolerance and D65 CIE-xy neutrality tolerance.
- Added standardized target matrices and CPU reference tests.
- Defined an OFX/shared-core architecture for real scopes, frame statistics and persistent reference-frame analysis instead of pretending a DCTL can provide those reductions.
- Frozen the first 114 M5 controls; existing combo selections remain compatible by unchanged prefix/index.
- Final M6 CI passes 149 tests with both Clang and GCC.

## 0.5.0-alpha.1 - 2026-09-24

M5 temporal film-texture implementation on `develop`.

- Added opt-in density-style multilayer grain after the print stage.
- Added artistic 8mm/16mm/35mm/65mm/Custom gauge scales, grain-size, roughness and RGB-layer color controls.
- Added independent shadow/midtone/highlight grain weighting.
- Added Static, Every Frame, Hold 2 and Hold 3 temporal modes driven by `TIMELINE_FRAME_INDEX` and `RAND`, plus a user seed.
- Added pre-negative Lens Soft and luminance-focused Micro Soft controls.
- Added Grain/Weight/Lens/Combined Texture View diagnostics.
- Frozen the first 99 M4 controls for saved-grade compatibility.
- Final M5 CI passes 134 tests with both Clang and GCC.

## 0.4.0-alpha.1 - 2026-09-24

- Added opt-in two-ring Halation, Bloom, Glow and Veiling Glare.
- Added Draft/Standard/High texture-sampling tiers and 2160-line radius scaling.
- Added independent thresholds, radii, halation tint and Optics View diagnostics.
- Switched the DCTL entry point to texture sampling while preserving the disabled M3 path.
- Added CPU texture/image tests. Spatial kernels remain original approximations, not measured PSFs.
- Final M4 CI passes 117 tests with both Clang and GCC.

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
