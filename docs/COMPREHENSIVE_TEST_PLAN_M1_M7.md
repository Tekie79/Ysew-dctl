# Yekermo Sew Film Lab — Comprehensive M1-M7 Resolve Acceptance Plan

Version under test: `0.7.0-alpha.4`  
Branch: `develop`  
DCTL code freeze commit: `f024f2e2d8a7dc74c08073c307d37d0edaa5696e`  
Plan: record the current documentation-only `develop` HEAD at test start  
Primary DCTL: `dist/YSEW_Film_Lab_M7_A4.dctl`

This is the formal end-of-development acceptance plan for milestones M1-M7. It replaces the
earlier incremental smoke tests. CPU/GCC/Clang validation has already passed; this plan tests the
actual DaVinci Resolve Studio host, Metal execution, real footage, cache/render behavior,
creative show decisions and Rec.709 delivery.

Do not merge to `main`, mark a candidate profile approved, or call the build production-ready
until the applicable release gates in this document are closed.

---

## 1. Acceptance model

Each test case receives one of these states:

| State | Meaning |
|---|---|
| PASS | Actual result matches the stated acceptance criteria. |
| WARN | Technically usable, but a documented deviation needs review before release. |
| FAIL | Acceptance criteria are not met. |
| BLOCKED | A prerequisite failed, so the test cannot produce valid evidence. |
| NOT RUN | Test has not been attempted. |
| N/A | Test does not apply to the final Yekermo Sew pipeline. |

Severity is separate from state:

| Severity | Meaning |
|---|---|
| B0 Blocker | Stop the comprehensive test until fixed: compile/UI failure, crash, corrupt output, invalid color-transform ownership, or nondeterministic render where determinism is required. |
| B1 Critical | Release blocker, but other independent tests may continue. |
| B2 Major | Must be resolved or explicitly accepted before production release. |
| Creative | Director/show decision rather than a software defect. |
| Informational | Recorded performance or observation with no preset threshold yet. |

A failed creative preference is not automatically a software failure. For example, changing the
Night profile because the shadows are too cool is a Creative revision; a hue discontinuity,
NaN/checkerboard in normal output, or skin-protection control that does nothing is a technical
failure.

---

## 2. Evidence directory and naming

Create one local evidence root outside the public repository:

```text
YSEW_M1-M7_ACCEPTANCE_YYYYMMDD/
├── 00_environment/
├── 01_m1_foundation/
├── 02_m2_input_wb/
├── 03_m3_film_model/
├── 04_m4_optics/
├── 05_m5_texture/
├── 06_m6_diagnostics/
├── 07_m7_show_mastering/
├── 08_performance_persistence/
├── 09_export_reimport/
├── logs/
└── report/
```

Evidence filenames should begin with the test ID, for example:

```text
M1-HOST-001_controls.png
M4-OPT-004_halation_window.mov
M5-GRN-006_rerender_A.exr
M5-GRN-006_rerender_B.exr
M7-EXP-003_export_settings.png
```

Do not commit production frames, unreleased footage, diagnostic logs containing private paths,
or reference stills to this public repository.

---

## 3. Environment capture — required before M1

### ENV-001 — Host identity
**Severity:** B0

Record:

- exact DaVinci Resolve Studio version and build;
- macOS version;
- computer model;
- GPU and Metal processing selection;
- RAM;
- timeline resolution / frame rate;
- pixel aspect ratio;
- monitoring/display path;
- viewer display-profile behavior if enabled;
- render cache, proxy and optimized-media state.

**Evidence:** screenshots of Resolve About/version, Memory and GPU settings, project Color
Management, timeline settings, and monitoring settings.

**PASS:** all requested fields are known. Unknown technical ownership of the test signal is not
accepted.

### ENV-002 — Build identity
**Severity:** B0

Run locally from the checked-out `develop` commit:

```bash
git rev-parse HEAD
shasum -a 256 dist/YSEW_Film_Lab_M7.dctl
python3 tools/build.py --check
python3 tools/release.py --check
```

Expected Git commit:

```text
86bdd8c4ef0023ee9c4e042919efe68d83ec7165
```

For this test-plan commit, the deterministic M7 package validated in CI as:

```text
YSEW_Film_Lab_0.7.0-alpha.3.zip
SHA-256 03874e98979f592a4295c094a8b1ed4c5b7b4da68a35776e9068b4862dc0ad14
bytes 45741
```

**PASS:** deterministic check succeeds and manifest still states:

```text
production_ready = false
host_acceptance = pending_comprehensive_resolve_test
```

Do not change these flags simply because the package builds.

---

# 6. Cross-milestone persistence and stress tests

## X-001 — Extreme-control sweep
**Severity:** B0 for crash/NaN; B2 for visual artifact

On duplicate synthetic and real clips, exercise min/max values for all major controls, one
family at a time.

**PASS:** no crash, frozen frame, NaN propagation, persistent checkerboard in normal output,
or corrupt cached result.

## X-002 — Enable/disable reversibility
**Severity:** B0

For Negative, Print, Film Model, Optics, Texture, Gamut Map and all contribution/diagnostic
views:

**PASS:** enable → change → disable returns to the correct bypass state with no stale buffer.

## X-003 — Node-instance independence
**Severity:** B0

Use two clips/nodes with different Film Lab settings.

**PASS:** changes to one instance do not modify the other.

## X-004 — Copy/paste grade
**Severity:** B1

Copy the Film Lab node/grade between clips.

**PASS:** all parameter values transfer correctly, including appended M2-M7 combo choices.

## X-005 — Project reopen
**Severity:** B0

After creating a mixed M1-M7 test state, save/quit/relaunch.

**PASS:** no missing DCTL, reset combo indices, stale old build selection or parameter loss.

---

# 7. Performance characterization

Performance is recorded, not silently converted into an arbitrary pass/fail threshold.

Use RF-01, RF-03 and RF-08 at minimum. Test 1080p and 4K if both matter to the production
workflow.

Record:

| Configuration | Playback FPS | Render sec/frame or total | Cache state | Notes |
|---|---:|---:|---|---|
| Film Lab bypass / control | | | | |
| Core M3 only | | | | |
| M4 Draft | | | | |
| M4 Standard | | | | |
| M4 High | | | | |
| M5 grain only | | | | |
| M4 Standard + M5 | | | | |
| Full intended candidate profile | | | | |

A crash, driver/GPU failure, unbounded memory growth or render inconsistency is B0. Slower-than-
real-time playback is recorded and then judged against the production workflow rather than
automatically failing.

---

# 8. Rec.709 export / re-import acceptance

## EXP-001 — Mastering configuration
**Severity:** B0

Before export:

```text
Output       = 709 Gamma 2.4
Diagnostics  = Off
Visual Guide = Off
Optics View  = Off
Texture View = Off
```

There must be no second downstream display transform.

Capture the complete node path and project/timeline color-management settings.

## EXP-002 — Lossless/near-lossless technical render
**Severity:** B0

Render a short reference sequence using a high-quality mastering/intermediate format suitable
for the test. Record codec/profile/bit depth, data levels, dimensions/fps, color-space/gamma
tags and all Advanced export settings.

Re-import into a clean unmanaged comparison timeline with no Film Lab/CST/LUT.

**PASS:** same-frame appearance and scopes match the baked source within the expected codec/
round-trip tolerance; no unexpected gamma shift, clipping, range error or double transform.

## EXP-003 — Grain rerender reproducibility
**Severity:** B0

Render the same frame range twice to a lossless image sequence with identical settings.

**PASS:** identical frame/seed/settings produce identical or numerically equivalent output
according to the chosen lossless path. Any difference must be explained before release.

## EXP-004 — Stress sequence
**Severity:** B1

Export a short sequence containing:

- deep shadows;
- practical/window highlights;
- saturated colors;
- skin;
- grain;
- optics;
- hard gradient/ramp.

**PASS:** no unexplained banding, temporal grain reset, cache seam, color-space jump, corrupted
frame or edge artifact.

---

# 9. Final release gates

M1-M7 acceptance is complete only when all five gates are explicitly decided.

## Gate A — Host / technical
Requires PASS for all B0 host, transform, persistence and deterministic-render tests.

## Gate B — Image-processing quality
Requires no unresolved B0/B1 defects in negative/print, optics, texture or diagnostics.

## Gate C — Creative show approval
Requires an explicit director decision for every Yekermo Sew profile intended for production.
A profile may be revised before approval; technical completion does not imply creative approval.

## Gate D — Performance / workflow
Requires the actual Resolve/Metal performance to be acceptable for the chosen grading/render
workflow. Record whether caching is required for Standard/High optics.

## Gate E — Rec.709 delivery
Requires correct output-transform ownership, QC review, export/re-import pass, diagnostic views
Off, expected data-level/tag behavior and approved monitoring review.

Only after Gates A-E close should a separate release change:

- candidate profile status;
- production-ready manifest state;
- release version/tag;
- or `main` branch.

M8/HDR is not required to close the M1-M7 Rec.709 release.

---

# 10. Minimum evidence to return for engineering review

At the end, provide one evidence bundle containing:

1. completed report template;
2. environment screenshots;
3. complete DCTL control-load recording;
4. numerical synthetic-fixture outputs;
5. representative look-review screenshots or short clips;
6. optics and grain temporal recordings;
7. performance table;
8. shot-match JSON/text reports;
9. export settings and clean re-import comparison;
10. Resolve diagnostic log only if a crash/GPU/compile failure occurred.

If a B0 failure occurs, return that evidence immediately; the remaining independent phases may
continue only when the failure does not invalidate their input assumptions.
