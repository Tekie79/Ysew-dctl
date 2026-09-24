# M2 technical input science

Version `0.2.0-alpha.1` adds explicit camera-log input transforms and a CAT02
white-balance path. It does **not** decode RAW. The selected Input must match the RGB gamut
and transfer function produced by the decoder or upstream converter.

## Supported inputs

| Input | Decode | Gamut conversion |
|---|---|---|
| DWG Intermediate | DaVinci Intermediate | Already DWG |
| DWG Linear | None | Already DWG |
| 709 Scene Linear | None | Rec.709/D65 to DWG/D65 |
| ARRI LogC4 | ARRI LogC4 Curve | AWG4/D65 -> XYZ -> DWG/D65 |
| Sony SLog3 Cine | S-Log3 | S-Gamut3.Cine/D65 -> XYZ -> DWG/D65 |
| Sony SLog3 G3 | S-Log3 | S-Gamut3/D65 -> XYZ -> DWG/D65 |
| RED Log3G10 | Log3G10 | REDWideGamutRGB/D65 -> XYZ -> DWG/D65 |

Sony's technical document defines S-Log3 as Full/Extended range in its described file/SDI
workflow. Resolve's data-level interpretation happens before the DCTL and must be correct.

## ProRes RAW boundary

ProRes RAW is not a unique RGB log/gamut declaration. Debayering occurs before this DCTL,
and a converter can choose its own RGB output. Record the converter's exact output gamma and
gamut. If it is not one of the camera choices above, use a verified upstream transform to
DWG Intermediate instead of selecting the closest-looking input.

## White balance

`WB Method = Legacy` is the default and preserves alpha numerical behavior. Existing Warmth
and Tint remain relative RGB adjustments.

`WB Method = CAT02` treats **WB Temp K** and **WB Duv** as the assumed source illuminant and
adapts that white to D65 in scene-linear XYZ. The CCT model uses a Planckian-locus approximation
at lower temperatures, the CIE daylight locus at higher temperatures and a smooth transition.
Duv is an offset in CIE 1960 UCS. `WB Strength` mixes unadapted and adapted scene values.

This is a colorimetric adaptation control. It is not a sensor calibration, a Kelvin estimator
from image pixels or a replacement for correctly interpreting RAW metadata. If the decoder
already applied camera white balance, do not apply the same correction twice.

`WB Method = Off` bypasses Legacy Warmth/Tint and CAT02 while retaining Exposure and RGB
Density controls.

## Reference tests

The CPU suite retains independent values from the manufacturer documents, including ARRI
LogC4 18% near 0.2784, Sony S-Log3 18% at 420/1023 and RED Log3G10 18% near 1/3. Published
or primaries-derived gamut matrices are tested independently. The final M2 commit passed
94 tests under both Clang and GCC.

Those tests validate shader math in the native CPU adapter. They do not establish Resolve,
Metal, playback or export compatibility.

## Host gate

Use a fresh `YSEW_Film_Lab_M2.dctl` instance for the next Resolve test. Existing menu
indices 0-2 and prior control IDs/defaults remain preserved; M2 appends camera choices and
four white-balance controls. Resolve Studio 21.1/Metal acceptance is still required before
the camera modes are used on production footage.
