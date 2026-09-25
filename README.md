# Yekermo Sew Film Lab

Custom DCTL development for the **Yekermo Sew** television series.

**Version:** `0.7.0-alpha.2` | **Development branch:** `develop` | **Milestone:** M7 show consistency and Rec.709 mastering

This is executable source, not a look LUT or a measured film-stock emulator. The develop branch now contains the M1-M7 technical feature set: camera/working-space transforms, balance/CAT02, parametric negative and print response, Yekermo Sew candidate looks, spatial optics, temporal grain/texture, advanced diagnostics, Rec.709 mastering QC, shot-consistency tooling and deterministic packaging. **Comprehensive Resolve/Metal, creative and delivery acceptance is still pending; do not treat this alpha as a production master grade.**

## Alpha.2 UI repair and graphical aids

Unquoted, concise labels; corrected menu declarations; hover tooltips; two native color pickers; and read-only tone, exposure-band, color/skin-range and vignette guides. The original 57 control IDs/types/defaults/enum order are retained; six controls are appended and optional behavior defaults Off. No draggable curve editor or OFX scope is claimed.

Start with [the UI retest](docs/UI_RETEST.md), using the two minimal probes and `dist/YSEW_Film_Lab_A2.dctl` (an exact version-named copy). See [graphical controls](docs/GRAPHICAL_CONTROLS.md) and the [sanitized host report](docs/validation/2026-09-24-host-alpha1.md). Color-picker/tooltips require Resolve 19.1 or later; the reported Studio 21.1 host is the current retest target.

## Current implementation

- Scene inputs: DaVinci Wide Gamut/Intermediate, linear DWG, or explicitly scene-linear Rec.709 primaries. Camera-native log must first be normalized using a verified upstream transform; ProRes RAW decoding is not implemented by a DCTL.
- Balance: exposure in stops, relative warm/cool and tint, and RGB density-point trims. These are not an absolute Kelvin meter or a calibrated printer.
- Creative stages: separately bypassable negative and print models, density-dependent RGB interaction, saturation, Neutral/Fall Interior/Winter Interior looks, and adjustable candidate-skin protection. Seasonal looks remain provisional until tuned against the series.
- Lens/output: feathered, movable vignette; original analytic SDR tone rendering; luminance-preserving compression toward the Rec.709 neutral axis; Gamma 2.4 encoding. Working-space output is available for an external renderer.
- Diagnostics: relative scene exposure/false color/zones, grayscale and RGB stop views, exposure ranges, output luminance/luma/hue/saturation/chroma, color-range masks, skin-candidate views, neutral-candidate chromatic bias, channel/volume warnings, compression amount, stage inspection, same-frame before/after and amplified differences. The exposure scale has numerical labels and an always-visible warning strip.

**Still outside the completed inline M1-M7 scope:** measured stock characterization, a real OFX frame-statistics/reference companion, HDR/additional qualified display outputs, and production delivery certification. See [the roadmap](docs/ROADMAP.md).

## Install and test

Use `dist/YSEW_Film_Lab_M7.dctl` for the comprehensive test; the canonical file remains `dist/YSEW_Film_Lab.dctl`. Read [Resolve setup](docs/RESOLVE_SETUP.md) before loading it. The default output is internally rendered **Rec.709 Gamma 2.4**; applying another output transform after it would be incorrect.

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

## M3 advanced film model

`Film Model → YS Advanced` enables the new opt-in negative/print response: neutral
density, density-inspired log-ratio color separation, exposure-dependent shadow/highlight
chroma, broad hue-family density biases, and independent print shadow/highlight trims.
Legacy remains the default for saved-grade compatibility. See
[M3 advanced film model](docs/M3_FILM_MODEL.md).

## M4 spatial optics

Opt-in Halation, Bloom, Glow and Veiling Glare now use neighboring-pixel texture
sampling with Draft/Standard/High quality tiers. All amounts default to zero and
Optics defaults Off. See [M4 spatial optics](docs/M4_SPATIAL_OPTICS.md).

## M5 film texture

`Texture` enables the new M5 layer: temporally deterministic density-style film grain,
gauge/size/roughness/color controls, exposure-dependent grain strength, pre-negative lens
softness and luminance micro-softness. Grain can be Static, Every Frame, Hold 2 or Hold 3.
All M5 processing defaults Off. See [M5 film texture](docs/M5_FILM_TEXTURE.md).

## M6 advanced diagnostics

M6 extends Diagnostics with Rec.709/P3-D65/Rec.2020 target-gamut status, normalized gamut
occupancy, RGB cube headroom, and scene calibration views for 18% gray, 90% white, 2% black
or a custom scene-linear reference. These are diagnostic targets only; normal mastering output
remains unchanged. See [M6 advanced diagnostics](docs/M6_ADVANCED_DIAGNOSTICS.md).

Frame-wide waveform/vectorscope/histogram/3D-cloud and persistent reference-frame comparison
are intentionally **not** faked inside the DCTL. Their proposed OFX/shared-core architecture is
defined in [M6 scope companion](docs/M6_SCOPE_COMPANION.md).

## M7 show consistency and mastering

M7 adds Night, Exterior Day and Exterior Dusk looks; versioned candidate whole-pipeline show
profiles; numerical reference/shot and episode-batch comparison; Rec.709 mastering-QC
diagnostics; and deterministic release packaging. Candidate profiles remain pending director
review. See [M7 show/mastering](docs/M7_SHOW_MASTERING.md) and the
[comprehensive delivery checklist](docs/DELIVERY_QC.md).

## Alpha.2 host-signature repair

Resolve Studio 21.1 rejected the M7 texture entry point with
`wrong argument int p_Width in Transform DCTL`. The M7 source used the documented parameter
types/names but formatted the entry across two lines without Blackmagic's exact spacing. The
developer documentation explicitly requires the main function definition exactly as shown.
Alpha.2 changes only the entry declaration formatting and related validation; pipeline math is
unchanged.

Use `dist/YSEW_Film_Lab_M7_A2.dctl` for the next host test. If it still fails, test
`dist/YSEW_Texture_Probe.dctl` to isolate host acceptance of the documented texture signature.
