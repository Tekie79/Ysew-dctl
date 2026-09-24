# M6 scope / reference-frame companion architecture

This document is the M6 evaluation result for functionality that should **not** be forced into
the Film Lab DCTL.

## Recommendation

Build a separate future `YSEW Film Scope` OFX analysis plugin backed by a shared color-math
core. Keep Film Lab responsible for rendering and per-pixel diagnostics; use the companion for
frame reductions, density scopes, persistent references and match statistics.

## Proposed components

### 1. Shared color core

Extract stable, host-neutral math for:

- declared input normalization;
- DWG/XYZ/Rec.709/P3-D65/Rec.2020 conversion;
- exposure and CIE-xy calibration measurements;
- skin/color candidate math where useful;
- target-gamut occupancy/headroom metrics.

The DCTL and OFX builds should consume the same generated constants/tests so target matrices
cannot drift independently.

### 2. GPU analysis pass

The OFX plugin receives the current frame and performs parallel reductions into fixed-size
buffers:

- RGB/luma histogram bins;
- waveform column/luminance density;
- RGB parade density;
- vectorscope hue/chroma density;
- target-gamut occupancy histogram;
- 3D RGB/gamut point-cloud reservoir sampling;
- exposure-zone counts;
- calibration pass/fail counts.

These are true frame statistics rather than image-space colors pretending to be statistics.

### 3. Reference-frame capture

A reference record should store:

- source clip/frame identity or user label;
- frame hash;
- declared source/working/output encoding;
- Film Lab version and relevant stage;
- analysis-profile version;
- numerical scope/statistic summaries;
- optional authorized reference image path or embedded thumbnail.

Default storage should favor metadata/statistics rather than copying production media.

### 4. Shot-match metrics

Initial matching should be **diagnostic, not automatic grading**. Compare current/reference:

- median and percentile exposure;
- shadow/midtone/highlight distribution;
- neutral chromatic bias;
- hue-sector occupancy;
- saturation distribution;
- candidate-skin exposure/chroma summary;
- target-gamut occupancy;
- black/highlight density summary.

The user should decide which differences are intentional. Automatic grade suggestions can be
a later, separately validated feature.

### 5. Synchronization

The companion should use timeline frame/timecode and explicit reference IDs. It must invalidate
analysis when the input frame, upstream grade, Film Lab version, working-space declaration or
analysis profile changes.

## Non-goals for the DCTL

Do not add fake:

- waveform curves built from only the current pixel;
- histogram counts without a reduction pass;
- persistent reference memory inside shader globals;
- shot matching based on one sampled color;
- 3D gamut clouds drawn from per-pixel guesses.

## Suggested implementation gate

Implement the OFX companion only after Film Lab's comprehensive Resolve/Metal test establishes
the final pipeline stages and identifies which stage(s) the scopes need to analyze. That avoids
binding a separate plugin to unstable intermediate semantics.
