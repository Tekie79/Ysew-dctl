# Primary references and provenance

Consulted during the 2026-09-24 foundation implementation. Specifications anchor technical conversion and terminology; they do not certify this implementation or the creative look.

**S1 - Blackmagic Design: DaVinci Wide Gamut Intermediate specification.**
https://documents.blackmagicdesign.com/InformationNotes/DaVinci_Resolve_17_Wide_Gamut_Intermediate.pdf
Pages 3-4 provide DWG primaries, D65, RGB/XYZ matrices, DI piecewise encoding/decoding and test mappings. Those pages were inspected visually as well as in extracted text. Published vectors, negative values, continuity and roundtrips are exercised by the native tests.

**S2 - ITU-R BT.709-6: HDTV parameter values.**
https://www.itu.int/rec/R-REC-BT.709
Reference for Rec.709 primaries, white point, signal terminology and delivery context. The code's XYZ matrices are primaries-derived; encoded Y-prime weights are not substituted for scene-linear DWG luminance weights.

**S3 - ITU-R BT.1886: Reference display electro-optical transfer function.**
https://www.itu.int/rec/R-REC-BT.1886
Reference for distinguishing display rendering/encoding from scene exposure. M1 uses an explicitly idealized pure Gamma 2.4 output and does not implement the complete nonzero-black BT.1886 model.

**S4 - Blackmagic Design: Resolve 19.1 New Features Guide.**
https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_19_1_New_Features_Guide.pdf
Printed page 5 points to Help > Documentation > Developer and describes DCTL random/timeline, alpha, color-picker, tooltip and error-dialog additions. It informs the roadmap; it is not proof that this shader has run in Resolve. Proprietary developer documentation and SDK binaries are not redistributed.

**CI dependency - GitHub actions/checkout v4.2.2, immutable commit.**
https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683
The commit was checked through the GitHub API. CI pins that version with read-only contents permissions and does not require repository write credentials for test execution.

The negative/print curves, RGB interaction proxy, provisional YS looks, gamut-knee function, diagnostic palettes and procedural digit glyphs are original project code. No commercial LUT, film scan, proprietary stock dataset, third-party DCTL implementation or model weight is included. Authentic stock profiling and licensing remain future work.

## Alpha.2 UI implementation references

The S4 Blackmagic 19.1 guide explicitly introduces native color pickers and hover tooltips. Primary source authored by Thatcher Freeman demonstrates unquoted control/menu labels and color-picker RGB member access:
https://github.com/thatcherfreeman/utility-dctls/blob/main/Effects/Process%20Negative%20Scans.dctl
Primary source authored by Moaz Elgabry demonstrates tooltip binding by the unquoted display label:
https://github.com/MoazElgabry/DCTLs/blob/main/ME_Localized%20Contrast.dctl
These were consulted for API spelling only. No color-transform, emulation or graphics algorithm was copied. The curves, glyphs and guides remain original project code. Their appearance in a CPU preview does not certify the target host UI.

**S5 - ARRI LogC4 specification, 23 January 2025.**
https://www.arri.com/resource/blob/278790/bea879ac0d041a925bed27a096ab3ec2/2022-05-arri-logc4-specification-data.pdf
Used for the LogC4 scene-linear transfer, negative-value handling, D65 white point and the
published AWG4-to-XYZ matrix.

**S6 - Sony Technical Summary for S-Gamut3.Cine/S-Log3 and S-Gamut3/S-Log3.**
https://pro.sony/s3/cms-static-content/uploadfile/06/1237494271406.pdf
Used for the S-Log3 reflection formula, code-value references, full-range convention and
published S-Gamut3.Cine/S-Gamut3 primaries. XYZ matrices are derived from those primaries
and D65.

**S7 - RED White Paper on REDWideGamutRGB and Log3G10, Rev C.**
https://docs.red.com/955-0187/PDF/915-0187%20Rev-C%20%20%20RED%20OPS,%20White%20Paper%20on%20REDWideGamutRGB%20and%20Log3G10.pdf
Used for Log3G10 equations/mapping values and the published REDWideGamutRGB-to-XYZ matrix.

**S8 - CAT02 / CIE colorimetry implementation.**
M2 applies the standard CAT02 transform in scene-linear XYZ. The user CCT white is generated
from documented Planckian/daylight chromaticity approximations and Duv is applied in CIE 1960
UCS. This is a colorimetric adaptation model, not sensor-specific camera calibration.

**S9 - Blackmagic Design: DaVinci Resolve 19.1 New Features Guide, DCTL RAND.**
https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_19_1_New_Features_Guide.pdf
The guide documents `RAND(uint p_Seed)` as a uniform random generator and explicitly notes
that `TIMELINE_FRAME_INDEX` can be used as a seed for temporally deterministic effects across
systems. M5 uses those facilities for grain phase generation. The CPU test shim deliberately
uses its own deterministic RAND surrogate; tests assert behavior rather than Blackmagic's
private generator sequence.
