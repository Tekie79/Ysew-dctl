# Development roadmap

A checked source milestone does not mean a production release. Every milestone must record mathematical, host, visual, and performance acceptance separately.

| Milestone | Scope | State |
|---|---|---|
| M0 | Repository inspection, `develop` branch and engineering contract | Established |
| M1 | Executable pointwise color pipeline, core diagnostics, tests and reproducible package | Implemented; alpha.1 host UI failed; alpha.2 UI repair and CPU checks complete, host retest pending |
| M2 | Actual Resolve/Metal acceptance; input/decoder verification; camera-native transforms with reference vectors; calibrated white-point adaptation; diagnostic legend/readout improvements | Technical implementation complete for ARRI LogC4, Sony S-Log3 and RED Log3G10 plus CAT02 WB; Resolve/Metal and actual decoder-output acceptance pending |
| M3 | Advanced negative/print response, color-density coupling, hue-dependent behavior, shadow/highlight controls and approved series look revisions; measured-stock profiles only with authorized data | Advanced parametric model implemented and 107-test dual-compiler CI passed; Resolve/Metal and final Yekermo Sew creative approval remain pending |
| M4 | Separate halation, bloom, lens glow and veiling glare; multi-radius spectral-weighted spatial kernels; quality/performance tiers and stage-contribution views | Implemented; 117-test dual-compiler CI passed. Comprehensive Resolve/Metal visual/performance acceptance deferred |
| M5 | Density-domain temporally deterministic multilayer grain; size/roughness/chroma and exposure response; resolution/frame/seed validation; optional lens softness and edge treatment | Implemented; 134-test dual-compiler CI passed. Resolve timeline/cache/render temporal validation and creative texture tuning deferred to comprehensive final test |
| M6 | Additional advanced diagnostics, validated destination-gamut options, color-volume tools, scene calibration profiles; evaluate OFX scopes/statistics/reference-frame companion | Inline M6 implemented and 149-test dual-compiler CI passed; OFX/statistics/reference-frame companion architecture defined but intentionally not implemented in the DCTL |
| M7 | Shot/scene matching workflow, director-approved fall/winter/night/exterior presets, episode consistency regression, Rec.709 mastering and delivery QC, packaging | Technical implementation complete: candidate profiles, metric comparison/batch regression, mastering-QC diagnostics and deterministic packaging. Director approval and comprehensive Resolve/delivery qualification pending |
| M8 | Optional additional display targets including HDR, with independent display rendering and delivery qualification | Future, not advertised as supported |

## Alpha.2 scope

UI metadata repair and optional graphical aids are implemented, not a new film-science milestone. Read [UI_RETEST.md](UI_RETEST.md). Native color pickers are interactive; the tone/range/vignette drawings are read-only and do not imply OFX widgets or statistics.

## Next execution gate

Run the comprehensive M1-M7 Resolve Studio / Metal acceptance plan in [DELIVERY_QC.md](DELIVERY_QC.md). Confirm the actual ProRes RAW converter output, GPU/UI behavior, optics/grain performance, candidate show-profile decisions, episode-consistency tolerances and Rec.709 export/re-import before any production-ready claim or promotion to `main`.

## Spatial and grain requirements

Halation must isolate highlight/edge behavior without washing the full image red. Bloom must remain distinct from film-base/emulsion scatter. Test an impulse, edge, constant field and bright practicals for energy, boundary sampling, radius scaling, tint and resolution independence. Do not promise an efficient large-radius single-node DCTL before profiling: texture sampling alone does not provide a cached multipass image graph.

Grain must be reproducible for the same frame/seed, change coherently across frames, survive seeks/cache/render, and have declared exposure and density domains. Resolve's documented RAND and timeline-frame facilities are candidates [S4], not yet used by M1. A film-gauge selector needs a defined spatial scale, not a renamed noise-amplitude preset.

Reference-frame matching and real scopes require access to image statistics/reference data outside the current pointwise transform. Define acquisition, storage, reference encoding, scope math and host synchronization before committing to a companion OFX implementation.

## Release gates

No release until the applicable tests, target GPU compilation, representative footage review, saved-grade compatibility, performance measurements, output-transform ownership, diagnostic-off export verification and delivery checks are documented. `main` remains unchanged unless the owner explicitly approves promotion.
