# Resolve setup and first host acceptance

**Alpha. The user reported an alpha.1 control-load failure; alpha.2 retesting is pending.**

Start with [UI_RETEST.md](UI_RETEST.md). Alpha.2 uses short labels and optional graphical controls; the old longer names below describe the same underlying controls. Its native picker/tooltips target Resolve 19.1 or later. Both Diagnostics and Visual Guide must be Off for export. Use a duplicate test timeline, never the only production grade. Back up the project first. The current API baseline is RGB Transform DCTL with classic controls plus native color pickers/tooltips; host-version compatibility must be verified on the actual installed build. Newer temporal/spatial work will have explicit version requirements.

## Install

Use Resolve's Open LUT Folder command from its color-management settings rather than guessing an operating-system path. Create a `YekermoSew` subfolder and copy `dist/YSEW_Film_Lab.dctl` into it. Refresh the LUT list as necessary, add ResolveFX DCTL to a Color node, and select the file. Confirm that the named controls appear and that there is no compiler error. Resolve's developer documentation is available under Help > Documentation > Developer [S4]. Record any complete compiler message instead of inferring success from the file appearing in a browser.

## Configuration A: internal Rec.709 rendering and diagnostics

Use an unmanaged **DaVinci YRGB** test pipeline with no external output transform, viewing/output LUT, automatic display tone mapping, or downstream creative node altering the diagnostic colors. A calibrated display and the operating system's viewing behavior remain your responsibility.

```text
Actual camera/decoder RGB
  -> verified input CST/normalization to DWG / DaVinci Intermediate
  -> shot correction as needed in the declared working domain
  -> YSEW Film Lab [Input: DWG Intermediate scene;
                    Output: Rec709 Gamma 2.4 internal output]
  -> output, with no second display conversion
```

Disable tone mapping and gamut mapping in a purely technical input CST where appropriate to retain scene data; a camera-specific input may still require correct camera normalization. Do not apply a display look LUT before this input and assume the result remains scene-linear after decoding. The selected DCTL input is the RGB encoding reaching that node, not necessarily the source camera setting. In a duplicate timeline, validate input CST settings against known reference values before interpreting stop maps.

ProRes RAW is a recording representation, not a unique RGB log/gamut choice. A decoder must produce RGB before the DCTL. The actual converter and its output log/gamut have not been established for this implementation. No camera-native input transform has been silently assumed.

## Configuration B: external color-managed output

In a correctly configured DWG/Intermediate working pipeline, select matching DWG/Intermediate input and **DWG Intermediate external output**, and keep Diagnostics **Off**. The external color-management system owns display rendering. An external renderer will not necessarily match the prototype internal SDR renderer's gray, contrast or gamut behavior. In this mode, output gray/gamut controls do not modify the working image.

Do not select internal Rec.709 rendering and then apply RCM/ACES/an additional CST output on top. Do not interpret output diagnostics as measurements of an external renderer: the DCTL cannot inspect downstream processing. For diagnostics, use a separate controlled test path following Configuration A rather than changing the production project's color management impulsively.

## First acceptance checklist

1. Record Resolve version/build/edition, OS, GPU model, selected compute backend, pixel aspect ratio, timeline and render dimensions, and actual source log/gamut. Load without compiler errors and inspect all controls.
2. Disable negative/print, set Neutral, zero balance/density/vignette. On verified scene-linear gray, 0.18 should read zero scene stops; 0.09 and 0.36 should read -1 and +1. In internal output, with these bypasses, neutral 0.18 should reach the selected gray code (default 0.42). Black should stay black and ramps should be smooth.
3. Exercise each diagnostic, both scene taps, every stage, grayscale, hue wrap at 0/360, range slider crossing, candidates, gamut excursions, and the numerical legend. Confirm that diagnostics in working-output mode warn rather than showing a measurement map.
4. Verify no-effect working-space identity and source-exposure independence from creative changes. Test saturated lights, near-black material, negative wide-gamut components, skin under mixed light and bright windows. Compare the source/balanced exposure taps intentionally.
5. Render short test clips at the series' actual dimensions and cadence. Compare export to viewer/reference monitor. Record playback/render time per frame; do not extrapolate CPU timings to a GPU performance claim.
6. Confirm diagnostic mode Off, output ownership, codec/data-level settings, metadata, scopes, legal delivery requirements and the final external review. The DCTL emits normalized RGB; do not bake 16-235 or 64-940 scaling into it and also request video-range export. Delivery settings own packing; a clamped RGB signal is not a complete broadcast certification.

## Look qualification material

Use representative source-frame/clip pairs with declared encoding: fall restaurant interior, cool/winter interior, practicals and windows, mixed lighting on different complexions, night shadows, exteriors, wardrobe and production-design colors. Preserve the original image and compare in a controlled display pipeline. Do not commit production media to this public repository; use authorized local fixtures or a private review channel.

References are in [SOURCES.md](SOURCES.md).

## M2 camera-input acceptance

Load a fresh `YSEW_Film_Lab_M2.dctl` after the alpha.2 UI gate passes. Confirm the appended
ARRI LogC4, Sony SLog3 Cine, Sony SLog3 G3 and RED Log3G10 choices plus WB Method, WB Temp K,
WB Duv and WB Strength.

For real camera footage, record the RAW decoder/converter name, version, output gamut, output
gamma and whether camera white balance has already been applied. Select a Film Lab camera input
only when the converter output matches that exact pair. Otherwise normalize upstream to DWG
Intermediate.

For controlled references with creative stages bypassed, ARRI LogC4 18% is approximately
0.2784, Sony S-Log3 18% is 420/1023, and RED Log3G10 18% is approximately 1/3. Each should
produce scene-relative zero stops. These checks validate the declared signal transform, not a
sensor's noise floor, clipping point or RAW metadata interpretation.
