# M1 validation record

Version: `0.1.0-alpha.1`  
Validation date: 2026-09-24  
Source and distribution SHA-256: `c8c3cdc1b91b8ccca0467246ac224c05e63396f46b763a446f3c46c3bb2b575d`

## Executed locally

| Check | Result |
|---|---|
| Reproducible package and UI lint | Passed; source and distribution byte-identical |
| Native CPU suite with Clang 17.0.0 | 43 tests passed |
| Native CPU suite with GCC 14.2.0 | 43 tests passed |
| Float32 shader source compiled with C++17, O2, Wall, Wextra, Werror | Passed under both compilers |
| Procedural false-color scale preview at 640x320 | Rendered through the native adapter and visually inspected; numeric -6 through +6 labels and warning strip visible |
| Python environment | Python 3.13.5; standard-library tests, no third-party test packages |

There are 43 unique tests, not 86 unique tests. Each compiler executes the same suite. The C++ adapter invokes the actual shader functions/entry point; it does not run Resolve or its DCTL preprocessor. The generated image is a synthetic test ramp, not series footage or a GPU result.

## Covered behavior

Published DI mapping vectors, signed log/linear roundtrips, piecewise continuity, DWG/XYZ values, D65/Rec.709 checks, matrix roundtrips, relative exposure references, photographic stop gains, density-point convention, negative curve gray anchor and monotonicity, signed working-space bypasses, output-gray calibration, tone monotonicity, gamut compression bounds and luminance preservation, input/balance diagnostic separation, nonpositive luminance, hue wrap, crossed range bounds, achromatic exclusion, candidate-skin mask behavior, working-output diagnostic guard, before/after difference, stage inspection, vignette center/edge, invalid-input flags, chromaticity versus brightness, warning stripe, stop quantization, all diagnostic modes, randomized controls, UI contract, reproducible source/distribution and procedural glyphs.

The suite contains seeded random tests: 300 matrix roundtrips, 500 candidate gamut samples with valid-luminance filtering, 80 input samples for each of 27 modes including Off, and 700 randomized-control renders. These are bounded synthetic tests, not proof of correctness over all possible inputs.

## Not executed / release blockers

Resolve host compilation and UI parsing; Metal, CUDA and OpenCL execution; macOS/Windows Resolve acceptance; actual camera-decoder roundtrip validation; production footage; saved-grade/keyframe migration behavior; GPU timing, cache and playback; calibrated display comparison; external color-management diagnostics; delivery codec/data-level/metadata/broadcast verification. Temporal and large-radius spatial effects are not present in M1.

The GitHub Actions workflow is configured to repeat the CPU tests on `develop`. Its remote execution status is separate from these local results; this record does not assert a successful GitHub runner execution.

## How to reproduce

```bash
python3 tools/build.py --check
CXX=clang++ python3 -m unittest discover -s tests -v
CXX=g++ python3 -m unittest discover -s tests -v
```

Record failures with the complete message and actual toolchain. Use [RESOLVE_SETUP.md](RESOLVE_SETUP.md) for the separate host acceptance gate. Do not describe this alpha as Resolve-tested, production-ready, physically calibrated, or real-time based on this record.
