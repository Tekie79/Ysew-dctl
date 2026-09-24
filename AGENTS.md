# Development contract

Work in `develop` unless the owner explicitly requests another branch. Do not push to `main`, merge, force-push, tag a production release, or open a PR to `main` without approval. Read the existing tree before changes and preserve concurrent work.

## Product direction

Build an advanced Yekermo Sew film imaging system, not a collection of generic LUTs. Preserve the series' restrained fall/winter interior direction: cool-neutral environments, controlled warm practicals, and skin preserved without a fixed brightness assumption. Presets remain provisional until the director approves tests on representative footage.

## Correctness rules

1. Every RGB boundary must declare its gamut, transfer function, and scene/display domain. Exactly one stage owns display rendering. Do not infer a camera or source gamma from the ProRes RAW codec.
2. Exposure diagnostics are relative scene-luminance stops, not sensor exposure, lux, ISO, aperture, or recoverability. Never label arbitrary shadows unusable or a middle-gray output code universal.
3. Hue/saturation masks are color candidates, not semantic face identification. A chromatic bias is not necessarily a white-balance error. Negative RGB in a wide gamut can be valid.
4. Keep unbounded/signed working values until the documented rendering boundary. Test zero, negative, near-zero, large, saturated, and nonfinite inputs.
5. Do not call mathematical RGB proxies measured photochemical or spectral emulations. Do not distribute commercial stock data or LUTs without permission.
6. DCTL control labels and combo display labels are unquoted raw tokens; only tooltip bodies use quoted strings. Use short labels and plain numeric literals inside UI macros. Validate full metadata, not merely the discarded C++ macro arguments. Pass all controls explicitly into helper functions. Keep DCTL UI identifiers, types, option ordering, and declaration ordering stable after publication; update the UI contract and document any breaking change.
7. Edit `src/YSEW_Film_Lab.dctl`; regenerate `dist` with `tools/build.py`. Never edit only the distribution copy. Keep source and distribution byte-identical.
8. A CPU adapter passing is not a Resolve/GPU pass. Record exact host version, operating system, GPU backend, dimensions and logs before making compatibility or real-time claims.
9. Spatial and temporal work must be benchmarked against quality, energy, radius, resolution, seed and timeline behavior. A local threshold tint is not halation. Noise is not automatically a film grain model.
10. A single stateless transform cannot promise frame-wide histograms, persistent reference-frame analysis, external output-stage inspection, or export blocking. Use a deliberate companion architecture where needed.

## Required checks

Run `python3 tools/build.py --check` and `python3 -m unittest discover -s tests -v`. Run both Clang and GCC when available. Keep the test adapter minimal and execute the shader itself. Add independent reference vectors and failure cases for new math; do not only mirror the implementation. Update `CHANGELOG.md`, the roadmap, and the validation record with actual outcomes and remaining gates.

Do not add a license, cloud dependency, external telemetry, uploaded series media, subscription requirement, or copied proprietary SDK without explicit approval.

## Host acceptance status

Alpha.1 failed control loading in the user-reported Studio 21.1 environment. Alpha.2 is a source/UI repair with optional read-only graphical guides; host retest remains pending. Never overwrite this status with a CPU pass. Run the minimal classic-control probe before attributing remaining missing controls to the camera, macOS or color management. See docs/UI_RETEST.md.

11. Camera-log inputs must match the exact decoder-output gamut and transfer function. Never infer an ARRI, Sony or RED encoding from a codec name or camera brand. Append Input enum values; never reorder existing saved indices.
12. CAT02 white balance is a declared source-white adaptation to D65, not an image-estimated illuminant or sensor calibration. Preserve Legacy as the default unless a deliberate compatibility break is approved.

13. M3 advanced film behavior is parametric. Do not call it Kodak, Fuji, 2383, 3513 or a measured stock unless licensed measurement data and a separate validated profile are actually added.
14. Preserve Film Model=Legacy as the default for existing grades. M3 UI controls are append-only; tests/ui_m2_compat.json freezes the first 67 controls.
15. Hue-family and density-separation controls must preserve neutral behavior where documented and must be stress-tested with signed wide-gamut inputs.

16. M4 spatial optics use finite neighborhood texture sampling. Never describe the ring kernel as a measured lens PSF, full Gaussian convolution or physically exact film-base scattering.
17. Optics must default Off and all spatial effect amounts default zero. Preserve the first 81 M3 controls.
18. Final Resolve testing must include GPU timing, frame boundaries, resolution scaling, cache/render consistency and real bright practicals/windows.

19. M5 gauge names are spatial-size presets only. Do not describe them as measured 8mm, 16mm, 35mm or 65mm stock unless measured reference data is later introduced.
20. Grain must remain deterministic for the same frame and seed, and temporal mode must use timeline-frame state rather than wall-clock randomness. The host RAND sequence does not need to match the CPU shim; behavioral invariants do.
21. Grain is applied as a multiplicative density-style perturbation after print, not as display-code additive noise. Texture defaults Off and the first 99 M4 controls remain frozen.
22. Comprehensive Resolve validation must test timeline seeks, render cache, re-render reproducibility, project reopen, frame-rate changes, resolution scaling, grain aliasing, performance and delivery renders.
