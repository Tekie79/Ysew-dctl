# Yekermo Sew Film Lab — Comprehensive M1-M7 Resolve Acceptance Plan

Version under test: `0.7.0-alpha.1`  
Branch: `develop`  
DCTL code freeze commit: `86bdd8c4ef0023ee9c4e042919efe68d83ec7165`  
Plan: record the current documentation-only `develop` HEAD at test start  
Primary DCTL: `dist/YSEW_Film_Lab_M7.dctl`

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
YSEW_Film_Lab_0.7.0-alpha.1.zip
SHA-256 8e43755aa4da3f85230429270df656c1dccd0b367a0d183bed9f26fb8b1be5c5
```

A locally generated ZIP should reproduce that hash when the tested tree matches the frozen plan
commit.

**PASS:** source commit, DCTL checksum, build check and release check are captured.

---

## 4. Test-project configuration

Create a new disposable Resolve project dedicated to acceptance. Do not change the production
Yekermo Sew project to make a test pass.

### Controlled internal-Rec.709 path

Use this configuration for numerical references and Film Lab diagnostics:

```text
Project color science: DaVinci YRGB
No project input LUT
No timeline/output LUT
No RCM/ACES automatic output rendering
No downstream CST/output transform
No group/timeline creative grade

Declared source / verified upstream normalization
       ↓
YSEW Film Lab M7
Input  = encoding actually arriving at the DCTL
Output = 709 Gamma 2.4
       ↓
Viewer / output
```

Diagnostics, Visual Guide, Optics View and Texture View are rendered pixels. Turn them Off before
normal-output and export comparisons.

A separate external-DWG-output test is included later.

---

## 5. Test material

Use both controlled synthetic material and representative Yekermo Sew footage.

### Synthetic fixtures

Prepare or reuse these fixtures:

| Fixture | Purpose |
|---|---|
| Neutral 0.09 / 0.18 / 0.36 DWG-linear patches | -1 / 0 / +1 scene-stop reference |
| Same patches encoded as DaVinci Intermediate | input-decode equivalence |
| -8 to +8 stop neutral ramp | exposure and curve monotonicity |
| 0 → high-value neutral ramp | toe/shoulder, clipping, output smoothness |
| RGB / CMY / neutral patches | hue, saturation, channel, gamut diagnostics |
| P3-D65 primary fixtures | Rec.709 versus P3 boundary tests |
| Rec.2020 primary fixtures | P3 versus Rec.2020 boundary tests |
| Constant bright field | optics invariance |
| Single bright point / small white square on black | halation/bloom/glow spread |
| Hard black/white edge | spatial kernel / edge-boundary behavior |
| Flat 18% and dark/highlight fields | grain distribution and temporal repeatability |
| Fine line / zone plate or high-frequency pattern | softness and grain aliasing |
| 18% gray, 90% white and 2% black patches | M6 calibration |

### Representative Yekermo Sew footage

Minimum real-footage set:

| ID | Material |
|---|---|
| RF-01 | Fall restaurant/interior with skin, practicals and window/highlight detail |
| RF-02 | Cool/winter interior |
| RF-03 | Night / low-key scene with deep shadow detail |
| RF-04 | Exterior day |
| RF-05 | Exterior dusk |
| RF-06 | Mixed color temperature / mixed practical-window lighting |
| RF-07 | Saturated wardrobe or production-design colors |
| RF-08 | Fine hair, skin texture and fabric detail for grain/softness |
| RF-09 | Bright practical or specular highlight for optics stress |
| RF-10 | Multiple skin tones in comparable lighting if available |

For every production clip used, record camera, source codec, decoder/converter, exact decoder
output gamut/gamma, upstream node settings and the DCTL Input selection.

---

# M1 — Foundation, host/UI, core transform and diagnostics

## M1-HOST-001 — DCTL load and control inventory
**Severity:** B0

Install a fresh copy as `YSEW_Film_Lab_M7.dctl`; refresh/restart Resolve as needed and add a
fresh ResolveFX DCTL instance.

**PASS:**

- no DCTL compiler/build error;
- all combo boxes, checkboxes, float/int sliders and both color pickers are visible;
- labels are concise and not surrounded by literal quotes;
- Input, Output, Diagnostics, Show Look, Film Model, Optics, Texture, Diag Gamut and M7 QC
  controls are present.

**Evidence:** full Settings-panel screen recording from top to bottom plus node graph.

If this fails, stop all downstream numerical tests and attach the complete compiler/UI evidence.

## M1-HOST-002 — Saved-control persistence
**Severity:** B0

Set recognizable non-default values, save, close Resolve, reopen the project and revisit the
same DCTL instance.

**PASS:** DCTL selection, combo choices, toggles, sliders and color-pickers retain their values.

## M1-COL-001 — DWG-linear neutral exposure reference
**Severity:** B0

Bypass creative stages:

```text
Input = DWG Linear
Negative = Off
Print = Off
Show Look = Neutral
Optics = Off
Texture = Off
Vignette = 0
Exposure/Warmth/Tint/Density RGB = 0
Output = 709 Gamma 2.4
Ref Gray = 0.18
```

With 0.09 / 0.18 / 0.36 patches:

**Expected scene exposure:** -1 / 0 / +1 stops.

With normal output, neutral 0.18 should reach encoded RGB approximately 0.42 with the bypassed
pipeline and default Output Gray.

**PASS:** stop readouts/diagnostic bands are correct and no hue is introduced into neutral
patches.

## M1-COL-002 — DaVinci Intermediate decode equivalence
**Severity:** B0

Compare identical scene values supplied once as DWG Linear and once as DWG Intermediate.

**PASS:** after choosing the matching Input mode, corresponding patches visually and numerically
match within practical floating-point/export tolerance.

Preferred evidence: float EXR output frames from both cases.

## M1-COL-003 — Exposure gain
**Severity:** B0

On verified scene-linear material:

- Exposure +1 must double scene-linear RGB before the creative model;
- Exposure -1 must halve it.

Use Source and Balanced measurement taps.

**PASS:** Source diagnostic is unchanged by Exposure; Balanced diagnostic moves by the requested
number of stops.

## M1-COL-004 — Working-output identity
**Severity:** B1

Use DWG-linear input, DWG-linear output and bypass all creative/spatial/texture/vignette stages.

**PASS:** signed working values—including valid negative wide-gamut components—survive without
unexpected clamp, gamut render or display gamma.

## M1-DIAG-001 — Core diagnostic sweep
**Severity:** B1

Exercise all original M1 modes 1-26, including:

- false color;
- EV gray/zones;
- exposure matte/overlay;
- RGB EV;
- output Y/Y-prime;
- hue/saturation/chroma;
- color/skin masks;
- neutral bias;
- non-positive RGB;
- pre-gamut/channel/volume checks;
- gamut amount;
- before/after/difference;
- stage view;
- invalid-input warning.

**PASS:** every mode displays, controls respond, warning stripe appears, and normal output returns
when Diagnostics=Off.

## M1-DIAG-002 — Working-output guard
**Severity:** B0

Select a working-space Output while a terminal diagnostic is active.

**PASS:** Film Lab shows its intentional warning behavior rather than silently returning
display-coded diagnostic colors into DWG.

---

# M2 — Camera input science and CAT02 white balance

## M2-IN-001 — Camera-transform reference values
**Severity:** B0 for any camera mode intended for production; otherwise N/A

With creative stages bypassed, verify:

| Input | 18% reference code | Expected decoded scene value |
|---|---:|---:|
| ARRI LogC4 / AWG4 | approximately 0.2784 | 0.18 |
| Sony S-Log3 | 420 / 1023 | 0.18 |
| RED Log3G10 | approximately 0.333333 | 0.18 |

**PASS:** each used transform yields zero scene-relative stops on its proper neutral reference.

## M2-IN-002 — Actual ProRes RAW converter ownership
**Severity:** B0

For the real Yekermo Sew ProRes RAW workflow record:

- decoder/converter product and version;
- output gamma/transfer function;
- output gamut;
- whether camera white balance is already applied;
- data-level interpretation;
- any upstream conversion node.

**PASS:** Film Lab Input exactly matches that RGB output, or the signal is explicitly normalized
upstream to a supported DWG representation. No guess based only on codec or camera brand.

## M2-WB-001 — CAT02 D65 identity
**Severity:** B0

Set WB Method=CAT02, WB Temp≈6504 K, Duv=0, Strength=1.

**PASS:** a D65-neutral signal remains neutral and unchanged within numerical tolerance.

## M2-WB-002 — CAT02 source-white correction
**Severity:** B1

Use a controlled warm source-white fixture or known chart measurement. Change WB Temp / Duv.

**PASS:** direction of correction is physically consistent, Strength=0 is identity, and Strength=1
is the full adaptation. No discontinuity while moving controls.

## M2-WB-003 — Legacy/off compatibility
**Severity:** B1

**PASS:** Legacy reproduces the old Warmth/Tint behavior; WB Method=Off ignores Warmth/Tint
while keeping Exposure and RGB Density active.

---

# M3 — Advanced negative and print response

## M3-MOD-001 — Legacy compatibility
**Severity:** B0

Keep Film Model=Legacy and move every M3-only advanced control through extreme values.

**PASS:** normal output does not change from the Legacy baseline solely because advanced controls
changed.

## M3-MOD-002 — Advanced negative/print bypass
**Severity:** B0

Test Negative and Print independently with Film Model=YS Advanced.

**PASS:** disabling either stage actually removes its contribution and produces no stale state.

## M3-MOD-003 — Neutral-ramp monotonicity
**Severity:** B0

Use a wide neutral exposure ramp through YS Advanced.

**PASS:** no reversal, flat step, NaN, color discontinuity, or visible banding caused by the
negative/print model.

## M3-MOD-004 — Negative density reference
**Severity:** B1

Neutralize the other advanced-color modifiers and set Neg Density=+0.20.

Reference:

```text
0.18 × 10^(-0.20) ≈ 0.11357
```

**PASS:** scene-linear neutral follows the documented density direction and approximate value.

## M3-MOD-005 — Neutral preservation / color separation
**Severity:** B1

Increase Neg Sep / Print Sep on neutral patches and chromatic patches.

**PASS:** neutrals remain neutral; chromatic patches show increased channel/color separation
without hue discontinuities or invalid values.

## M3-MOD-006 — Shadow/highlight chroma selectivity
**Severity:** B1

Compare the same chromatic signal at deep-shadow, midtone and strong-highlight exposures while
varying Neg Shadow Sat / Neg High Sat.

**PASS:** controls act predominantly in their intended exposure regions.

## M3-CREATIVE-001 — Skin-protection behavior
**Severity:** B2 / Creative

Use real skin under neutral and mixed light.

**PASS:** increasing Skin Protect reduces the Show Look contribution on selected candidates but
does not create hard mask edges, exclude darker skin only because of luminance, or imply face
detection. Note false-positive objects separately.

---

# M4 — Spatial optics

## M4-OPT-001 — Constant-field invariance
**Severity:** B0

Enable each optical effect individually on a uniform bright field.

**PASS:** no visible spatial contribution is added to a truly constant field beyond floating
precision.

## M4-OPT-002 — Isolated-highlight spread
**Severity:** B1

Use a white point/square on black.

**PASS:** each effect spreads into neighboring dark pixels and disappears when its Amount=0.

## M4-OPT-003 — Effect separation
**Severity:** B1

Inspect one at a time:

- Halation: red/orange edge contribution;
- Bloom: more source-colored broadband spread;
- Glow: larger and more neutral;
- Veiling Glare: widest and most neutral.

**PASS:** controls are perceptually distinguishable and do not all look like the same blur.

## M4-OPT-004 — Halation quality
**Severity:** B2 / Creative

On RF-01/RF-03/RF-09:

**PASS:** no full-frame red wash, no obvious discrete ring pattern at normal viewing size,
no colored stair-stepping around windows/practicals, and Hal Tint moves red↔orange in the
intended direction.

## M4-OPT-005 — Frame-boundary behavior
**Severity:** B1

Move bright sources against all four frame edges/corners.

**PASS:** no wraparound, crash, black seam, sampling garbage or opposite-edge contamination.

## M4-OPT-006 — Resolution consistency
**Severity:** B2

Test 1080p and 4K using identical normalized content/settings.

**PASS:** perceived normalized radii remain reasonably consistent; document expected small
differences from finite integer sampling.

## M4-PERF-001 — Quality-tier performance
**Severity:** Informational initially; B2 if operationally unusable

Record playback FPS and render time for:

- Optics Off;
- Draft;
- Standard;
- High.

Use the same clip, resolution, cache state and viewer settings.

No real-time threshold is assumed in advance. Record whether Draft/Standard are practically
usable and whether High requires caching/rendering.

---

# M5 — Film grain, texture and lens softness

## M5-GRN-001 — Same-frame/seed determinism
**Severity:** B0

Every Frame mode, fixed frame and fixed seed.

**PASS:** repeated visits/renders of the same timeline frame produce the same grain realization.

## M5-GRN-002 — Temporal cadence
**Severity:** B0

**Expected:**

- Static: same grain at all frames;
- Every Frame: changes every frame;
- Hold 2: frames 0/1 share a pattern, 2/3 share a new pattern;
- Hold 3: frames 0/1/2 share a pattern, 3/4/5 share a new pattern.

Test around edits and non-zero timeline starts as well.

## M5-GRN-003 — Seed behavior
**Severity:** B1

**PASS:** changing Grain Seed changes the pattern without changing the rest of the grade.

## M5-GRN-004 — RGB-layer grain
**Severity:** B2

On neutral 18%:

- Grain Color=0 should remain essentially channel-correlated/neutral;
- higher Grain Color may separate R/G/B microstructure but must not create objectionable colored
  blotches.

## M5-GRN-005 — Exposure-dependent grain
**Severity:** B1

Set Shadow=0, Mid=100, High=0.

**PASS:** deep shadow and strong highlight grain contribution are strongly suppressed while
midtone grain remains.

Repeat with each region emphasized individually.

## M5-GRN-006 — Cache, seek and rerender reproducibility
**Severity:** B0

Test:

- arbitrary forward/backward seeks;
- render cache generation;
- clearing/rebuilding cache;
- parameter change followed by cache invalidation;
- project save/reopen;
- two lossless/float repeated renders.

**PASS:** same frame/seed/settings are reproducible after each operation. Compare lossless EXR
renders numerically or by hash when the entire output pipeline is deterministic.

## M5-GRN-007 — Resolution and aliasing
**Severity:** B1

Compare 1080p and 4K at 100% pixel view and normal viewing distance.

**PASS:** grain scale behaves consistently with the normalized-size design and does not show
unacceptable moiré, crawling or checker patterns.

## M5-TEX-001 — Lens Soft
**Severity:** B1

Use a hard edge / fine-detail fixture and RF-08.

**PASS:** local high-frequency detail softens smoothly; no edge echo or color fringe is
introduced.

## M5-TEX-002 — Micro Soft
**Severity:** B1

**PASS:** luminance microcontrast is reduced while more chromatic relation is retained than with
a simple RGB blur.

---

# M6 — Advanced gamut and calibration diagnostics

## M6-GAM-001 — Rec.709 / P3-D65 / Rec.2020 target ordering
**Severity:** B1

Use known target-primary fixtures.

**Expected examples:**

- a P3-D65 red primary is outside Rec.709 but on/near the P3-D65 boundary;
- a Rec.2020 green primary is outside P3-D65 but on/near the Rec.2020 boundary.

**PASS:** Target Gamut reflects that ordering.

## M6-GAM-002 — Gamut Occupancy
**Severity:** B1

**Expected interpretation:**

- neutral ≈ 0 occupancy;
- target boundary ≈ 1;
- materially >1 shown as outside/magenta.

Test neutral and increasingly saturated patches.

## M6-GAM-003 — RGB Headroom
**Severity:** B1

**PASS:** central neutral values show more headroom than near-boundary values; outside-target
values show the outside warning.

## M6-CAL-001 — 18% gray calibration
**Severity:** B0

Cal Profile=18 Gray, Source tap.

**PASS:** exact 0.18 is green; 0.09 reports under; 0.36 reports over.

## M6-CAL-002 — 90% white / 2% black
**Severity:** B1

**PASS:** exact 0.90 and 0.02 reference patches pass their respective profiles within the
configured EV tolerance.

## M6-CAL-003 — D65 neutrality
**Severity:** B1

Use a verified D65-neutral patch and a deliberately tinted patch.

**PASS:** neutral is within configured CIE-xy tolerance; tinted sample moves to amber/red.

This is a chromaticity-distance check, not Delta E and not semantic neutral detection.

## M6-CAL-004 — Combined calibration
**Severity:** B1

Verify all four combinations:

- exposure pass + neutral pass;
- exposure fail only;
- neutral fail only;
- both fail.

**PASS:** colors/states follow the documented M6 mapping.

---

# M7 — Show looks, consistency workflow, Rec.709 QC and packaging

## M7-LOOK-001 — Look-mode availability and switching
**Severity:** B1

Verify all six modes:

```text
Neutral
Fall Interior
Winter Interior
Night
Exterior Day
Exterior Dusk
```

**PASS:** all modes switch without stale state, corruption or unexpected change to technical
Input/Output ownership.

## M7-LOOK-002 — Candidate whole-pipeline profiles
**Severity:** B1 / Creative

Validate profiles:

```bash
python3 tools/show_profiles.py validate
python3 tools/show_profiles.py list
```

Apply each profile manually or through your chosen preset-transfer workflow to the corresponding
RF material.

For every profile record one decision:

- APPROVE;
- REVISE;
- REJECT.

Record exact parameter revisions and reference timecodes.

**Release gate:** all profiles actually intended for Yekermo Sew must receive an explicit
director decision. The repository status must remain `pending_director_review` until then.

## M7-LOOK-003 — Cross-profile intent
**Severity:** Creative

Check that:

- Night is cooler / lower chromatic energy than Exterior Day;
- Exterior Day remains comparatively restrained;
- Exterior Dusk has stronger cool-ambient / warm-highlight separation;
- Fall and Winter remain visually distinct;
- skin remains believable across all intended profiles.

This test is an artistic acceptance, not a numerical winner/ranking.

## M7-MATCH-001 — Shot/reference comparator
**Severity:** B1

Use validated metric JSON at the same stage and working space.

Run:

```bash
python3 tools/shot_match.py compare \
  --reference REF.json \
  --candidate SHOT.json
```

**PASS:** known within-tolerance fixture returns PASS; known moderate deviation returns WARN;
known >2× tolerance deviation returns FAIL.

## M7-MATCH-002 — Stage/working-space guard
**Severity:** B0

Attempt mismatched stage and mismatched working-space comparisons.

**PASS:** tool rejects the comparison rather than producing a misleading score.

## M7-MATCH-003 — Episode batch
**Severity:** B1

Run an episode manifest against an approved category reference.

**PASS:** all shots are included, aggregate status reflects the worst item, and each WARN/FAIL
can be traced to its individual metric deltas.

Human review is required before changing a grade; numerical mismatch is not automatic evidence
that the shot is artistically wrong.

## M7-QC-001 — QC Pre Gamut
**Severity:** B1

Use in-gamut, near-boundary and out-of-gamut Rec.709 test colors.

**PASS:** green / amber / red mapping follows the configured QC Margin.

## M7-QC-002 — QC Final Range
**Severity:** B1

**PASS:** final internally rendered signal reports target-cube proximity after the gamut step
without altering normal output.

## M7-QC-003 — QC Master priority
**Severity:** B1

Verify priority:

1. materially outside pre-gamut → red;
2. otherwise compression > QC threshold → orange;
3. otherwise inside but near boundary → yellow;
4. otherwise → green.

## M7-PKG-001 — Deterministic release package
**Severity:** B0

Run twice:

```bash
python3 tools/release.py --check
python3 tools/release.py --check
```

For the frozen plan commit, expected validated M7 package metadata is:

```text
YSEW_Film_Lab_0.7.0-alpha.1.zip
SHA-256 8e43755aa4da3f85230429270df656c1dccd0b367a0d183bed9f26fb8b1be5c5
bytes 47213
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
