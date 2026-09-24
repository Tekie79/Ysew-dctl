# M7 show consistency and Rec.709 mastering

Version `0.7.0-alpha.1` closes the planned SDR feature-development sequence before the
comprehensive Resolve test. It adds candidate Yekermo Sew show profiles, numerical shot/scene
consistency comparison, mastering-QC views and deterministic release packaging.

## Show looks

The DCTL `Show Look` menu now preserves the original indices and appends:

| Index | Look | Status |
|---:|---|---|
| 0 | Neutral | Existing |
| 1 | Fall Interior | Candidate |
| 2 | Winter Interior | Candidate |
| 3 | Night | Candidate |
| 4 | Exterior Day | Candidate |
| 5 | Exterior Dusk | Candidate |

Night reduces chromatic energy while increasing cool-shadow separation. Exterior Day is the
least stylized of the new modes. Exterior Dusk increases cool ambient / warm-highlight
separation. All modes retain the existing candidate-skin protection behavior.

These values are **candidate show settings**, not director-approved finals. Approval must happen
during representative-footage review. The repository must not change
`approval_status: pending_director_review` until that review is explicitly completed.

## Candidate whole-pipeline profiles

`presets/yekermo_sew_show_profiles_v1.json` contains five creative starting profiles:

- fall_interior
- winter_interior
- night
- exterior_day
- exterior_dusk

Each profile contains creative negative/print/look/optics/texture settings. It deliberately
excludes technical controls such as Input, Output and Diagnostics. This prevents a creative
preset from silently changing color-management ownership.

Validate or inspect profiles with:

```bash
python3 tools/show_profiles.py validate
python3 tools/show_profiles.py list
python3 tools/show_profiles.py show night
```

The values are starting points for the final review, not measured stock behavior.

## Shot / scene consistency workflow

M7 does not fake persistent frame statistics inside the DCTL. The comparison workflow consumes
a versioned **shot metrics** JSON record produced by a future scope companion, another trusted
analysis process, or manually verified measurements.

The schema is:

`schemas/ysew-shot-metrics-v1.schema.json`

A record identifies the shot, measurement stage and working space, then supplies metrics such
as median exposure, shadow/highlight percentiles, neutral chromaticity error, median saturation,
candidate-skin exposure, target-gamut occupancy and black/highlight levels.

Compare one candidate against a reference:

```bash
python3 tools/shot_match.py compare \
  --reference reference.json \
  --candidate candidate.json
```

Use `--format json` for machine-readable output.

For an episode batch, create:

```json
{
  "version": 1,
  "reference": "reference.json",
  "shots": ["shot_001.json", "shot_002.json"]
}
```

Then run:

```bash
python3 tools/shot_match.py batch --manifest episode_manifest.json
```

The provisional tolerances live in
`presets/yekermo_sew_consistency_v1.json`. A metric is PASS within its tolerance, WARN between
1x and 2x tolerance, and FAIL above 2x. These tolerances are engineering starting points; the
final series thresholds require footage review.

Stage and working-space mismatches are rejected rather than compared.

## Rec.709 mastering QC

M7 appends three diagnostics:

### QC Pre Gamut

Inspects the internally rendered **linear Rec.709 signal before gamut compression**.

- green: inside with more than the configured margin;
- amber: near a 0/1 target cube face;
- red: materially outside the Rec.709 cube.

### QC Final Range

Inspects the final internally rendered Gamma-2.4 output after decoding it back to linear light.
This view shows whether the delivered internal render sits near an RGB cube boundary after the
Film Lab gamut step.

### QC Master

Combined decision aid:

- red: pre-gamut signal materially outside Rec.709;
- orange: gamut-compression amount exceeds `QC Comp x1k`;
- yellow: signal is inside but within `QC Margin x1k` of a cube face;
- green: none of those conditions is triggered.

Defaults:

```text
QC Margin x1k = 10   -> 0.010 linear RGB
QC Comp x1k   = 50   -> 0.050 compression amount
```

These diagnostics are **not broadcast legalization**. Resolve export data levels, codec packing,
container tags and downstream transformations remain delivery settings outside this DCTL.

## Release package

`tools/release.py` creates a deterministic ZIP containing the M7 DCTL, core instructions,
show profiles, consistency tolerances, schema and comparison tool.

Validate without retaining an artifact:

```bash
python3 tools/release.py --check
```

Create the package locally:

```bash
python3 tools/release.py
```

The ZIP embeds a SHA-256 manifest, marks `production_ready=false`, and records host acceptance
as pending the comprehensive Resolve test.

M7 packaging does not mean the software is production-qualified.

## Final approval boundary

The next gate is the comprehensive Resolve Studio / Metal test, followed by director review of
representative Yekermo Sew footage and delivery qualification. Only after those gates pass
should candidate show profiles be marked approved or a production release be considered.
