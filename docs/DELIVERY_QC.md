# Comprehensive Resolve and Rec.709 delivery QC

This checklist is the planned end-of-development acceptance sequence for Yekermo Sew Film Lab.
Passing CPU CI is necessary but not sufficient.

## 1. Host / UI acceptance

Record:

- exact DaVinci Resolve Studio version and build;
- macOS version;
- Mac/GPU model and Metal processing mode;
- timeline resolution and frame rate;
- display/output monitoring path.

Load a **fresh** `YSEW_Film_Lab_M7.dctl` instance.

Confirm all combo boxes, checkboxes, sliders and color pickers display correctly with concise,
unquoted labels. Confirm no DCTL compiler message.

## 2. Technical input science

Using controlled reference signals, verify DWG/Intermediate and DWG-linear behavior, then test
each camera transform that will actually be used.

For ProRes RAW material, record the decoder/converter and its exact RGB output gamut/gamma.
Never select a camera mode merely because it resembles the source camera brand.

Verify:

- 18% scene gray maps to zero scene-relative stops;
- CAT02 D65 identity;
- exposure-stop behavior;
- no double input or output transform.

## 3. Core film model

Test Legacy and YS Advanced separately.

Use neutral ramps, saturated patches and real material to inspect:

- monotonic toe/shoulder response;
- neutral preservation;
- negative/print density;
- shadow/highlight chroma behavior;
- hue-family response;
- gamut compression behavior.

Do not label the parametric model as a measured stock.

## 4. Candidate show profiles

Use representative footage from:

- fall restaurant/interior;
- winter/cool interior;
- night;
- exterior day;
- exterior dusk;
- mixed practical/window light;
- different skin tones, wardrobe and production-design colors.

Review profile values in `presets/yekermo_sew_show_profiles_v1.json`.

For each profile record:

- approve / revise / reject;
- required parameter changes;
- reference frames/timecodes;
- intended scene categories.

Only then change `approval_status` from `pending_director_review`.

## 5. Spatial optics

Inspect isolated bright practicals, windows, hard edges and constant fields at actual timeline
resolution.

Check Halation, Bloom, Glow and Veiling Glare individually and combined for:

- radius and boundary behavior;
- unwanted red wash;
- halos;
- edge clamping;
- resolution consistency;
- Draft/Standard/High performance.

Record playback/render timing for Optics Off and each quality tier.

## 6. Grain and texture

At 100% pixel view and normal viewing size, test:

- Static / Every Frame / Hold 2 / Hold 3;
- same-frame/seed reproducibility;
- timeline seeks;
- render cache;
- cache invalidation after parameter changes;
- project close/reopen;
- repeated renders;
- 1080p and 4K;
- actual delivery frame rate;
- faces, hair, fabric and fine production-design detail.

Look specifically for temporal crawling, colored noise artifacts and sub-pixel aliasing.

## 7. Diagnostics

Exercise every diagnostic mode and confirm:

- source versus balanced measurement tap;
- false-color legend;
- color/skin range masks;
- P3-D65 / Rec.2020 target diagnostics;
- calibration profiles;
- M7 QC modes;
- optics/texture contribution views;
- warning stripe behavior.

Confirm diagnostic/reference colors are being viewed through the controlled terminal Rec.709
path and not changed by a downstream transform.

## 8. Shot / episode consistency

Choose approved reference shots for each relevant scene category.

Acquire shot metrics at the same stage and working space. Run:

```bash
python3 tools/shot_match.py compare --reference REF.json --candidate SHOT.json
python3 tools/shot_match.py batch --manifest EPISODE.json
```

Review WARN/FAIL items visually. Numerical differences are review cues, not automatic grading
instructions. Intentional dramatic changes should remain intentional.

Tune `yekermo_sew_consistency_v1.json` only from reviewed evidence.

## 9. Rec.709 mastering

For internal mastering:

```text
Output = 709 Gamma 2.4
Diagnostics = Off
Visual Guide = Off
Optics View = Off
Texture View = Off
```

There must be no second CST/RCM/ACES/output LUT applying another display transform after Film
Lab.

Run QC Pre Gamut, QC Final Range and QC Master before returning Diagnostics to Off.

Check Resolve scopes and the calibrated monitoring path separately.

## 10. Export / re-import

Render representative and stress-test sequences.

Record:

- codec/profile/bit depth;
- dimensions and frame rate;
- Resolve data levels;
- color-space/gamma tags;
- output transform ownership;
- render speed.

Re-import the baked output into a clean unmanaged comparison path with no Film Lab/CST/LUT.
Compare the same frames in Resolve.

Verify black/white behavior, gradients, practicals, saturated colors, grain temporal behavior
and absence of unexpected clipping/banding.

## 11. Release package

Run:

```bash
python3 tools/build.py --check
python3 -m unittest discover -s tests -v
python3 tools/release.py --check
```

Create the ZIP only after those pass.

Verify its `manifest.json` hashes and confirm it still states
`production_ready=false` until host, creative and delivery approval are explicitly recorded.

## 12. Promotion gate

Do not merge to `main`, mark profiles director-approved, or call the build production-ready
until the comprehensive evidence is recorded and the remaining blockers are explicitly closed.
