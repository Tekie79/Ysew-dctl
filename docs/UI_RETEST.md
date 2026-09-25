# Alpha.2 UI repair: repeat Test 1 first

Use **YSEW_Film_Lab_A2.dctl** for this retest. It is byte-identical to the canonical
`YSEW_Film_Lab.dctl`, but the distinct name makes the new version easier to select
and reduces ambiguity with the earlier `_test` copy. The alpha.1 file was verified
correctly in the supplied report; this is not a claim that the user installed it
incorrectly. Do not delete a file referenced by existing grades.

## What changed

UI labels and menu labels are now unquoted raw tokens. All control labels are 16
characters or shorter. UI numeric arguments use plain literals. The original 57
variable IDs, types, numeric defaults and enum ordering are retained. Optional new
controls are appended, and all new processing/guide switches default Off. Full
explanations have moved into hover tooltips and the documentation.

The previous CPU adapter accepted UI metadata without validating it. The new
source linter rejects quoted control/menu labels, malformed choices, numeric
suffixes in UI arguments and other contract errors. That is a source validation
improvement, not a simulation of Resolve's UI creation.

## Install without changing the project configuration

Copy the three files below into a separate `YekermoSew_A2` subfolder of the LUT
folder opened from Resolve. Refresh the list or restart Resolve. Use a **fresh
temporary ResolveFX DCTL instance on a test clip/node**, not just the earlier
cached alpha.1 instance. Keep your chosen test timeline; this UI-only check does
not require changing project or timeline color management. Do not alter production
grades. Do not stack the probes and Film Lab together.

1. **YSEW_UI_Probe_A2.dctl** isolates the original control classes. Expect `Gain`
   (float slider), `Steps` (integer slider), `View` (Input / Gray / Steps menu), and
   `Enabled` (checkbox), all without visible quotation marks. Choose View=Steps:
   changing Steps should change the band count; unchecking Enabled returns the
   input. A host may arrange controls by type rather than source order; inspect
   the whole panel.
2. **YSEW_Color_Probe_A2.dctl** isolates graphical controls. Expect `Test Color`,
   `View` (Input / Swatch), and `Enabled`. Choose a different color in the native
   color dialog; Swatch should show those RGB numbers. Hover Test Color for its
   tooltip. This is not a color-calibration test.
3. **YSEW_Film_Lab_A2.dctl** is the repaired full alpha. Expect 63 custom controls:
   46 float sliders, 1 integer slider, 8 menus, 6 checkboxes and 2 color pickers.
   Verify Input, Output, Show Look, Diagnostics, Measure, Stage, EV Steps and
   Visual Guide, plus Negative, Print, Gamut Map, EV Legend, Pick Range Hue and
   Pick Skin Hue. Menus or checkboxes may be lower in the host's panel.

**Stop at the first missing control or build error.** A minimal probe failure is
more useful than continuing numerical tests with an unknown configuration. If the
basic probe succeeds but the full plugin fails, report that distinction; do not
assume all UI defects share one cause.

## Graphical check after controls load

On a known test signal, use Output=709 Gamma 2.4 and an unmanaged terminal path.
Leave Diagnostics=Off and select a Visual Guide. Tone Curve, Exposure Band, Color
Range and Skin Range draw an upper-right read-only panel; Vignette draws boundary
rings and a center crosshair. Adjust their existing sliders to see the guides
change. Do not try to drag these drawings. The native color swatches are the
interactive controls. See [GRAPHICAL_CONTROLS.md](GRAPHICAL_CONTROLS.md).

Set **both Diagnostics=Off and Visual Guide=Off before export**. Guides are rendered
pixels and the warning stripe is not an export blocker. A guide in either DWG
output mode deliberately produces the working-space warning instead of an
incorrectly encoded display overlay.

## Resume numerical tests only after setup is verified

The supplied host report leaves timeline overrides, LUTs, group/timeline nodes,
GPU preference and cache/proxy state unverified. None of that explains literal
quote characters in labels. However, audit those settings before scoring the
EXR numerical tests. Do not use the ramp checkerboard observation as a failed
color-science measurement.

The existing A/B/C/D EXRs remain usable; no replacement signals are required.
For A/C/D select Input=DWG Linear. For B select Input=DWG Intermediate. Use
Output=709 Gamma 2.4, Negative=Off, Print=Off, Show Look=Neutral, zero balance,
density and vignette, Diagnostics=Off and Visual Guide=Off. Source scene exposure
is now selected by `Measure=Source`; the balanced tap is `Measure=Balanced`.
The former Scene exposure grayscale menu item is now `Scene EV Gray`.

## Evidence to return

A short recording or screenshots showing the basic probe's View menu and Enabled
checkbox, the color probe's swatch, and the full plugin's Input/Output/Diagnostics
controls are enough for this gate. Record which file is selected, which control
is missing, whether a fresh effect instance was used, and any complete build-error
text. No crash occurred in the initial report, so a large diagnostic log is not
needed unless a new crash/GPU/build failure warrants one. The exact Resolve build
and explicitly selected GPU backend remain helpful but are not substitutes for
showing the repaired controls.

Host status: alpha.1 control-load failure reported; **alpha.4 Resolve retest pending**.

## Studio layout order

For the full Film Lab alpha.4 control-load check, confirm this top-to-bottom order:

`Input -> Balance/WB -> Negative -> Show Look/Skin -> Print -> Optics -> Texture/Grain ->
Vignette -> Diagnostics/Calibration/QC -> Output`.

Input must be first and Output must be last.

## Timeline frame probe

Load `YSEW_Timeline_Frame_Probe.dctl` separately.

- If it compiles and the noise changes as the timeline advances, record PASS.
- If it fails on `TIMELINE_FRAME_INDEX`, record the complete build error. Film Lab alpha.4
  should still compile because its main grain path has a static compatibility fallback.

This probe result determines whether Every Frame / Hold grain modes can be accepted on the
current Resolve/Metal host.
