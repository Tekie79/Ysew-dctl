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
