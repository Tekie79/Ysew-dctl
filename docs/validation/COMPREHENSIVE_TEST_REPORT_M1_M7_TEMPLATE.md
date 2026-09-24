# Yekermo Sew Film Lab — M1-M7 Comprehensive Test Report

Test date:  
Tester:  
Film Lab version: `0.7.0-alpha.1`  
Git commit: `86bdd8c4ef0023ee9c4e042919efe68d83ec7165`  
DCTL SHA-256:  
Release ZIP SHA-256:  

## 1. Environment

| Field | Actual value |
|---|---|
| Resolve Studio version/build | |
| macOS version | |
| Computer | |
| GPU / processing mode | |
| RAM | |
| Display / monitoring path | |
| Project color science | |
| Timeline color space | |
| Output color space / gamma | |
| Timeline resolution | |
| Timeline frame rate | |
| Pixel aspect | |
| Cache state | |
| Proxy / optimized media | |
| LUTs / downstream transforms | |

## 2. ProRes RAW / source pipeline

| Field | Actual value |
|---|---|
| Camera | |
| Source codec | |
| Decoder / converter | |
| Decoder version | |
| Output gamut | |
| Output gamma / transfer | |
| White balance already applied? | |
| Data-level interpretation | |
| Upstream CST/DCTL | |
| Film Lab Input selection | |
| Film Lab Output selection | |

## 3. Test result matrix

Use only: `PASS`, `WARN`, `FAIL`, `BLOCKED`, `NOT RUN`, `N/A`.

| Test ID | Severity | Status | Evidence | Notes / actual result |
|---|---|---|---|---|
| ENV-001 | B0 | | | |
| ENV-002 | B0 | | | |
| M1-HOST-001 | B0 | | | |
| M1-HOST-002 | B0 | | | |
| M1-COL-001 | B0 | | | |
| M1-COL-002 | B0 | | | |
| M1-COL-003 | B0 | | | |
| M1-COL-004 | B1 | | | |
| M1-DIAG-001 | B1 | | | |
| M1-DIAG-002 | B0 | | | |
| M2-IN-001 | B0/N/A | | | |
| M2-IN-002 | B0 | | | |
| M2-WB-001 | B0 | | | |
| M2-WB-002 | B1 | | | |
| M2-WB-003 | B1 | | | |
| M3-MOD-001 | B0 | | | |
| M3-MOD-002 | B0 | | | |
| M3-MOD-003 | B0 | | | |
| M3-MOD-004 | B1 | | | |
| M3-MOD-005 | B1 | | | |
| M3-MOD-006 | B1 | | | |
| M3-CREATIVE-001 | B2/Creative | | | |
| M4-OPT-001 | B0 | | | |
| M4-OPT-002 | B1 | | | |
| M4-OPT-003 | B1 | | | |
| M4-OPT-004 | B2/Creative | | | |
| M4-OPT-005 | B1 | | | |
| M4-OPT-006 | B2 | | | |
| M4-PERF-001 | Info/B2 | | | |
| M5-GRN-001 | B0 | | | |
| M5-GRN-002 | B0 | | | |
| M5-GRN-003 | B1 | | | |
| M5-GRN-004 | B2 | | | |
| M5-GRN-005 | B1 | | | |
| M5-GRN-006 | B0 | | | |
| M5-GRN-007 | B1 | | | |
| M5-TEX-001 | B1 | | | |
| M5-TEX-002 | B1 | | | |
| M6-GAM-001 | B1 | | | |
| M6-GAM-002 | B1 | | | |
| M6-GAM-003 | B1 | | | |
| M6-CAL-001 | B0 | | | |
| M6-CAL-002 | B1 | | | |
| M6-CAL-003 | B1 | | | |
| M6-CAL-004 | B1 | | | |
| M7-LOOK-001 | B1 | | | |
| M7-LOOK-002 | B1/Creative | | | |
| M7-LOOK-003 | Creative | | | |
| M7-MATCH-001 | B1 | | | |
| M7-MATCH-002 | B0 | | | |
| M7-MATCH-003 | B1 | | | |
| M7-QC-001 | B1 | | | |
| M7-QC-002 | B1 | | | |
| M7-QC-003 | B1 | | | |
| M7-PKG-001 | B0 | | | |
| X-001 | B0/B2 | | | |
| X-002 | B0 | | | |
| X-003 | B0 | | | |
| X-004 | B1 | | | |
| X-005 | B0 | | | |
| EXP-001 | B0 | | | |
| EXP-002 | B0 | | | |
| EXP-003 | B0 | | | |
| EXP-004 | B1 | | | |

## 4. Performance

| Configuration | Resolution | FPS | Playback FPS | Render time | Cache state | Notes |
|---|---|---:|---:|---:|---|---|
| Film Lab bypass/control | | | | | | |
| Core M3 | | | | | | |
| M4 Draft | | | | | | |
| M4 Standard | | | | | | |
| M4 High | | | | | | |
| M5 grain only | | | | | | |
| M4 Standard + M5 | | | | | | |
| Final candidate profile | | | | | | |

## 5. Candidate show-profile decisions

| Profile | Decision: APPROVE / REVISE / REJECT | Reference clip/timecode | Required changes | Notes |
|---|---|---|---|---|
| Fall Interior | | | | |
| Winter Interior | | | | |
| Night | | | | |
| Exterior Day | | | | |
| Exterior Dusk | | | | |

Do not edit repository `approval_status` until the decision is explicit.

## 6. Shot / episode consistency

Reference shot(s):  

Metric stage:  
Working space:  

| Episode / scene | Reference | Candidate count | PASS | WARN | FAIL | Notes |
|---|---|---:|---:|---:|---:|---|
| | | | | | | |

Attach the generated shot-match text/JSON outputs.

## 7. Export / re-import

| Field | Value |
|---|---|
| Codec / profile | |
| Bit depth | |
| Resolution / FPS | |
| Data levels | |
| Color-space tag | |
| Gamma tag | |
| Output transform owner | |
| Render time | |
| Re-import comparison result | |

Repeated lossless render comparison / hashes:

```text
Render A:
Render B:
Comparison:
```

## 8. Defects / deviations

For every FAIL or WARN:

### DEFECT-___
Test ID:  
Severity:  
Repeatability:  
Expected:  
Actual:  
Exact steps:  
Control values:  
Frame/timecode:  
Evidence filename(s):  
Resolve log filename, if applicable:  
Workaround, if any:  

## 9. Release gates

| Gate | PASS / FAIL / PENDING | Evidence / decision |
|---|---|---|
| A — Host / technical | | |
| B — Image-processing quality | | |
| C — Creative show approval | | |
| D — Performance / workflow | | |
| E — Rec.709 delivery | | |

## 10. Final disposition

Overall status: `PASS / FAIL / PENDING`

Production-ready approved? `YES / NO`

Approved profiles:  

Known limitations accepted for release:  

Remaining blockers:  

Decision owner:  

Decision date:  

Do **not** merge to `main`, mark profiles approved or change the package manifest to
`production_ready=true` until the release-gate decision is explicit.
