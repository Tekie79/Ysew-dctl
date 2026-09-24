# Changelog

## 0.1.0-alpha.1 - 2026-09-24

Initial M1 implementation on `develop`, branched from the existing `main` commit `479211485d88915edb7e7b892e1c21cb85de97e1`.

Added original color-pipeline DCTL with three scene-input encodings, three output modes, balance/density controls, negative and print curve prototypes, provisional fall/winter looks, candidate-skin protection, vignette, SDR rendering, gamut compression, 26 diagnostic modes, and a numerical scene-exposure legend. Added a reproducible distribution, 43 native-code CPU tests, a stable UI declaration contract, and development/host-validation documentation.

Local Clang 17 and GCC 14.2 CPU tests passed. Resolve DCTL parsing, Metal/CUDA/OpenCL execution, playback, actual footage, monitoring and delivery remain unvalidated. The full spatial/temporal film pipeline is not yet implemented.
