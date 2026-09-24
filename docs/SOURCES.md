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
