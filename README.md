# Yekermo Sew Film Lab

Custom DCTL development for the **Yekermo Sew** television series.

**Version:** `0.2.0-alpha.1` | **Development branch:** `develop` | **Milestone:** M2 technical input science

This is executable source, not a look LUT or a finished film-stock emulator. The first vertical slice implements scene transforms, balancing, original parametric negative/print responses, provisional seasonal looks, vignette, SDR rendering, and 26 diagnostic modes. Alpha.1 failed the user's first Resolve control-load test. Alpha.2 repairs the declarations and adds optional graphical aids; its 76 CPU/source tests pass, but **Resolve retesting is pending. Do not use it as a production master grade yet.**

## Alpha.2 UI repair and graphical aids

Unquoted, concise labels; corrected menu declarations; hover tooltips; two native color pickers; and read-only tone, exposure-band, color/skin-range and vignette guides. The original 57 control IDs/types/defaults/enum order are retained; six controls are appended and optional behavior defaults Off. No draggable curve editor or OFX scope is claimed.

Start with [the UI retest](docs/UI_RETEST.md), using the two minimal probes and `dist/YSEW_Film_Lab_A2.dctl` (an exact version-named copy). See [graphical controls](docs/GRAPHICAL_CONTROLS.md) and the [sanitized host report](docs/validation/2026-09-24-host-alpha1.md). Color-picker/tooltips require Resolve 19.1 or later; the reported Studio 21.1 host is the current retest target.

## Current implementation

- Scene inputs: DaVinci Wide Gamut/Intermediate, linear DWG, or explicitly scene-linear Rec.709 primaries. Camera-native log must first be normalized using a verified upstream transform; ProRes RAW decoding is not implemented by a DCTL.
- Balance: exposure in stops, relative warm/cool and tint, and RGB density-point trims. These are not an absolute Kelvin meter or a calibrated printer.
- Creative stages: separately bypassable negative and print models, density-dependent RGB interaction, saturation, Neutral/Fall Interior/Winter Interior looks, and adjustable candidate-skin protection. Seasonal looks remain provisional until tuned against the series.
- Lens/output: feathered, movable vignette; original analytic SDR tone rendering; luminance-preserving compression toward the Rec.709 neutral axis; Gamma 2.4 encoding. Working-space output is available for an external renderer.
- Diagnostics: relative scene exposure/false color/zones, grayscale and RGB stop views, exposure ranges, output luminance/luma/hue/saturation/chroma, color-range masks, skin-candidate views, neutral-candidate chromatic bias, channel/volume warnings, compression amount, stage inspection, same-frame before/after and amplified differences. The exposure scale has numerical labels and an always-visible warning strip.

**Not implemented yet:** camera-native IDTs, calibrated chromatic adaptation, measured negative/print stock responses, spatial halation/bloom/glow, animated grain, lens softness, actual frame statistics/scopes, reference-frame shot matching, HDR output, or delivery certification. See [the roadmap](docs/ROADMAP.md).

## Install and test

Use `dist/YSEW_Film_Lab_A2.dctl` for this retest; the canonical file remains `dist/YSEW_Film_Lab.dctl`. Read [Resolve setup](docs/RESOLVE_SETUP.md) before loading it. The default output is internally rendered **Rec.709 Gamma 2.4**; applying another output transform after it would be incorrect.

For development, Python 3.10+ and Clang or GCC with C++17 support are sufficient; there are no third-party Python dependencies.

```bash
python3 tools/build.py
python3 tools/build.py --check
python3 -m unittest discover -s tests -v
# Optional: exercise another CPU compiler.
CXX=g++ python3 -m unittest discover -s tests -v
```

Turn both Diagnostics and Visual Guide Off before delivery. Visual guides are rendered pixels, not export-safe host widgets.

The test harness compiles and calls the actual DCTL source through a small float32 C++ adapter. It does not merely test a separate Python reimplementation. It also does not replace Resolve's DCTL parser or a Metal/CUDA/OpenCL acceptance test.

## Documentation

[Architecture](docs/ARCHITECTURE.md) explains the stage and color-domain contracts. [Diagnostics](docs/DIAGNOSTICS.md) defines every mode, unit, limitation, and warning. [Resolve setup](docs/RESOLVE_SETUP.md) covers output ownership and host testing. [Validation](docs/VALIDATION.md) records what was actually tested. [Roadmap](docs/ROADMAP.md) tracks the full-film pipeline. [Sources](docs/SOURCES.md) identifies the public specifications used.

Keep development on `develop`. Do not merge, force-push, or open a PR to `main` without approval. Do not commit production footage, reference stills, proprietary LUTs, credentials, or SDK copies. No project-wide open-source license has been selected; public repository visibility alone is not a license grant.

## M2 technical input science

The current `develop` build adds explicit ARRI LogC4/AWG4, Sony S-Log3/S-Gamut3.Cine,
Sony S-Log3/S-Gamut3 and RED Log3G10/REDWideGamutRGB input transforms. It also adds an
optional CAT02 CCT/Duv white-balance path. These are transforms for already-decoded RGB;
they do not debayer or identify ProRes RAW automatically. Legacy Warmth/Tint remains the
default for saved-grade compatibility. See [M2 input science](docs/M2_INPUT_SCIENCE.md).
