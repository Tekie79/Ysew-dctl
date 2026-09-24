# Comprehensive Resolve and Rec.709 delivery QC

The authoritative executable M1-M7 plan is now
[COMPREHENSIVE_TEST_PLAN_M1_M7.md](COMPREHENSIVE_TEST_PLAN_M1_M7.md), with the fillable
[report template](validation/COMPREHENSIVE_TEST_REPORT_M1_M7_TEMPLATE.md).

This shorter file remains a release-gate summary.

## Required final gates

1. Host/UI/Metal acceptance on the exact M7 build.
2. Technical input/output ownership including the actual ProRes RAW decoder output.
3. Negative/print, optics and grain image-quality acceptance.
4. M6 diagnostics/calibration validation.
5. Explicit director decision on every production show profile.
6. Shot/episode consistency review using like-for-like metrics.
7. Rec.709 QC plus export/re-import acceptance.
8. Deterministic package validation with diagnostics/guides Off by default.

Run:

```bash
python3 tools/build.py --check
python3 -m unittest discover -s tests -v
python3 tools/release.py --check
```

Do not promote to `main` or mark the package production-ready until Gates A-E in the
comprehensive report are explicitly closed.
