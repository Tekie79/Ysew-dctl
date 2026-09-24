# Yekermo Sew Film Lab

Custom DCTL development for the **Yekermo Sew** television series.

**Version:** `0.1.0-alpha.1` | **Development branch:** `develop` | **Milestone:** M1 foundation

This is executable source, not a look LUT or a finished film-stock emulator. The first vertical slice implements scene transforms, balancing, original parametric negative/print responses, provisional seasonal looks, vignette, SDR rendering, and 26 diagnostic modes. It has passed local CPU tests. **It has not yet been compiled or visually qualified inside DaVinci Resolve. Do not use it as a production master grade yet.**

## Current implementation

- Scene inputs: DaVinci Wide Gamut/Intermediate, linear DWG, or explicitly scene-linear Rec.709 primaries. Camera-native log must first be normalized using a verified upstream transform; ProRes RAW decoding is not implemented by a DCTL.
- Balance: exposure in stops, relative warm/cool and tint, and RGB density-point trims. These are not an absolute Kelvin meter or a calibrated printer.
- Creative stages: separately bypassable negative and print models, density-dependent RGB interaction, saturation, Neutral/Fall Interior/Winter Interior looks, and adjustable candidate-skin protection. Seasonal looks remain provisional until tuned against the series.
- Lens/output: feathered, movable vignette; original analytic SDR tone rendering; luminance-preserving compression toward the Rec.709 neutral axis; Gamma 2.4 encoding. Working-space output is available for an external renderer.
- Diagnostics: relative scene exposure/false color/zones, grayscale and RGB stop views, exposure ranges, output luminance/luma/hue/saturation/chroma, color-range masks, skin-candidate views, neutral-candidate chromatic bias, channel/volume warnings, compression amount, stage inspection, same-frame before/after and amplified differences. The exposure scale has numerical labels and an always-visible warning strip.

**Not implemented yet:** camera-native IDTs, calibrated chromatic adaptation, measured negative/print stock responses, spatial halation/bloom/glow, animated grain, lens softness, actual frame statistics/scopes, reference-frame shot matching, HDR output, or delivery certification. See [the roadmap](docs/ROADMAP.md).

## Install and test

Use `dist/YSEW_Film_Lab.dctl`. Read [Resolve setup](docs/RESOLVE_SETUP.md) before loading it. The default output is internally rendered **Rec.709 Gamma 2.4**; applying another output transform after it would be incorrect.

For development, Python 3.10+ and Clang or GCC with C++17 support are sufficient; there are no third-party Python dependencies.

```bash
python3 tools/build.py
python3 tools/build.py --check
python3 -m unittest discover -s tests -v
# Optional: exercise another CPU compiler.
CXX=g++ python3 -m unittest discover -s tests -v
```

The test harness compiles and calls the actual DCTL source through a small float32 C++ adapter. It does not merely test a separate Python reimplementation. It also does not replace Resolve's DCTL parser or a Metal/CUDA/OpenCL acceptance test.

## Documentation

[Architecture](docs/ARCHITECTURE.md) explains the stage and color-domain contracts. [Diagnostics](docs/DIAGNOSTICS.md) defines every mode, unit, limitation, and warning. [Resolve setup](docs/RESOLVE_SETUP.md) covers output ownership and host testing. [Validation](docs/VALIDATION.md) records what was actually tested. [Roadmap](docs/ROADMAP.md) tracks the full-film pipeline. [Sources](docs/SOURCES.md) identifies the public specifications used.

Keep development on `develop`. Do not merge, force-push, or open a PR to `main` without approval. Do not commit production footage, reference stills, proprietary LUTs, credentials, or SDK copies. No project-wide open-source license has been selected; public repository visibility alone is not a license grant.
