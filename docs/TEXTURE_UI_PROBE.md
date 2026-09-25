# Resolve 21 texture-UI probe

Use `YSEW_Texture_UI_Probe.dctl` to determine which DCTL UI widget types Resolve Studio 21.1
renders when the DCTL uses the same texture Transform signature as Film Lab.

Expected controls, in order:

1. Float Slider
2. Int Slider
3. Value Box
4. Check Box
5. Combo Box
6. Color Picker

If only sliders/value boxes appear while Check Box / Combo Box / Color Picker are absent, that
is a host/path limitation or bug independent of Film Lab's layout. Capture one screenshot.

Also compare against the existing pointwise `YSEW_UI_Probe_A2.dctl` and
`YSEW_Color_Probe_A2.dctl`. If those show combo/check/color controls while the texture probe
does not, the limitation is specific to the texture-transform DCTL path.

Do not continue the full comprehensive test until Input/Output ownership is selectable in the
main Film Lab UI or an explicit compatibility UI is implemented.
