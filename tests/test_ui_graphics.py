"""UI syntax regressions, native picker/probe bindings, and optional guide behavior."""
from __future__ import annotations
from collections import Counter
import json
import math
from pathlib import Path
import random
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from ui_schema import parse_ui
from build import SOURCE, outputs, validate
from native import Shader

class UISchemaTests(unittest.TestCase):
    def test_control_type_inventory(self):
        ui=parse_ui(SOURCE.read_text())
        self.assertEqual(len(ui),114)
        self.assertEqual(Counter(c.kind for c in ui),{
            'DCTLUI_SLIDER_FLOAT':64,'DCTLUI_SLIDER_INT':25,
            'DCTLUI_COMBO_BOX':15,'DCTLUI_CHECK_BOX':8,'DCTLUI_COLOR_PICKER':2})

    def test_short_unquoted_labels(self):
        for c in parse_ui(SOURCE.read_text()):
            self.assertLessEqual(len(c.label),16)
            self.assertNotIn('"',c.label)
            for option in c.choices:self.assertNotIn('"',option)

    def test_reject_old_quoted_float_label(self):
        with self.assertRaisesRegex(ValueError,'unquoted'):
            parse_ui('DEFINE_UI_PARAMS(gain, "Gain", DCTLUI_SLIDER_FLOAT, 1.0, 0.0, 2.0, 0.01)')

    def test_reject_gpu_reserved_local_identifier(self):
        text = SOURCE.read_text()
        self.assertIn('float hue_half_width =', text)
        with self.assertRaisesRegex(ValueError, 'GPU-reserved'):
            validate(text.replace('float hue_half_width =', 'float half ='))

    def test_reject_old_quoted_checkbox_label(self):
        with self.assertRaisesRegex(ValueError,'unquoted'):
            parse_ui('DEFINE_UI_PARAMS(enabled, "Enabled", DCTLUI_CHECK_BOX, 1)')

    def test_reject_quoted_combo_choices(self):
        with self.assertRaisesRegex(ValueError,'unquoted'):
            parse_ui('DEFINE_UI_PARAMS(mode, Mode, DCTLUI_COMBO_BOX, 0, {A, B}, {"Input", "Output"})')

    def test_reject_numeric_suffix_in_ui(self):
        with self.assertRaisesRegex(ValueError,'suffixes'):
            parse_ui('DEFINE_UI_PARAMS(gain, Gain, DCTLUI_SLIDER_FLOAT, 1.0f, 0.0, 2.0, 0.01)')

    def test_reject_combo_count_and_default(self):
        for text in [
            'DEFINE_UI_PARAMS(mode, Mode, DCTLUI_COMBO_BOX, 0, {A, B}, {Input})',
            'DEFINE_UI_PARAMS(mode, Mode, DCTLUI_COMBO_BOX, 2, {A, B}, {Input, Output})',
            'DEFINE_UI_PARAMS(mode, Mode, DCTLUI_COMBO_BOX, 0, {A, A}, {Input, Output})']:
            with self.assertRaises(ValueError):parse_ui(text)

    def test_validate_tooltip_target_and_quoted_body(self):
        line='DEFINE_UI_PARAMS(gain, Gain, DCTLUI_SLIDER_FLOAT, 1.0, 0.0, 2.0, 0.01)\n'
        parse_ui(line+'DEFINE_UI_TOOLTIP(Gain, "A tooltip, with a comma.")')
        with self.assertRaises(ValueError):parse_ui(line+'DEFINE_UI_TOOLTIP(Unknown, "Description")')
        with self.assertRaises(ValueError):parse_ui(line+'DEFINE_UI_TOOLTIP(Gain, Unquoted description)')

    def test_reject_duplicate_controls(self):
        line='DEFINE_UI_PARAMS(enabled, Enabled, DCTLUI_CHECK_BOX, 1)\n'
        with self.assertRaises(ValueError):parse_ui(line+line)

    def test_preserve_v1_ids_types_defaults_and_enum_order(self):
        old=json.loads((ROOT/'tests/ui_v1_compat.json').read_text())
        current=parse_ui(SOURCE.read_text())
        self.assertEqual(len(old),57)
        for before,after in zip(old,current):
            self.assertEqual(before['name'],after.name)
            self.assertEqual(before['type'],after.kind)
            self.assertEqual(before['default'],float(after.values[0]))
            self.assertEqual(before['enum'],list(after.enums)[:len(before['enum'])])

    def test_probe_control_inventories(self):
        basic=parse_ui((ROOT/'src/YSEW_UI_Probe_A2.dctl').read_text())
        color=parse_ui((ROOT/'src/YSEW_Color_Probe_A2.dctl').read_text())
        self.assertEqual({c.kind for c in basic},{'DCTLUI_SLIDER_FLOAT','DCTLUI_SLIDER_INT','DCTLUI_COMBO_BOX','DCTLUI_CHECK_BOX'})
        self.assertEqual(len(basic),4)
        self.assertEqual(len(color),3)
        self.assertEqual(sum(c.kind=='DCTLUI_COLOR_PICKER' for c in color),1)

    def test_all_distribution_files_are_exact(self):
        for path,data in outputs().items():
            self.assertEqual(path.read_bytes(),data)

    def test_all_optional_features_default_off(self):
        ui={c.name:c for c in parse_ui(SOURCE.read_text())}
        for key in ['range_pick_on','skin_pick_on','guide_mode','optics_on','optics_view','texture_on','texture_view']:
            self.assertEqual(ui[key].default,'0')

class GraphicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.s=Shader()
    @classmethod
    def tearDownClass(cls):cls.s.temp.cleanup()
    def setUp(self):
        self.s.reset();self.s.set(input_mode=1,diag_legend=0)
    def assertRGB(self,a,b,tol=3e-6):
        for aa,bb in zip(a,b):self.assertTrue(math.isclose(aa,bb,rel_tol=tol,abs_tol=tol),(a,b))

    def test_alpha1_numerical_regression(self):
        fixture=json.loads((ROOT/'tests/fixtures/alpha1_pixels.json').read_text())
        self.assertEqual(len(fixture['cases']),64)
        for case in fixture['cases']:
            self.s.reset();self.s.set(**case['controls'])
            self.assertRGB(self.s.pixel(case['input']),case['output'],tol=1e-5)

    def test_picker_rgb_hue(self):
        for rgb,expected in [((1,0,0),0),((0,1,0),120),((0,0,1),240),((.70,.42,.175),28)]:
            self.assertAlmostEqual(self.s.scalar(9,*rgb,17),expected,delta=1e-4)

    def test_picker_neutral_and_invalid_fallback(self):
        for rgb in [(0,0,0),(.5,.5,.5),(1,1,1),(1.1,.2,0),(-.1,.2,.2),(float('nan'),.2,.1)]:
            self.assertEqual(self.s.scalar(9,*rgb,37),37)

    def test_disabled_pickers_do_not_change_grade_or_mask(self):
        for mode in [0,1,13,15,16]:
            self.s.set(diag_mode=mode,look_mode=2)
            before=self.s.pixel((.18,.09,.06))
            self.s.set(range_pick=(0,1,0),skin_pick=(0,0,1))
            self.assertRGB(self.s.pixel((.18,.09,.06)),before)

    def test_range_picker_matches_manual_hue(self):
        for rgb in [(1,.1,.05),(.1,.5,.02),(.04,.1,.8),(.18,.18,.18)]:
            self.s.set(diag_mode=13,range_hue=120,range_pick_on=0)
            expected=self.s.pixel(rgb)
            self.s.set(range_hue=23,range_pick_on=1,range_pick=(0,1,0))
            self.assertRGB(self.s.pixel(rgb),expected)

    def test_skin_picker_matches_manual_hue(self):
        rgb=self.s.vector(3,(.18,.09,.06))
        for mode in [0,15,16]:
            self.s.set(diag_mode=mode,diag_tap=1,look_mode=2,skin_hue=28,skin_pick_on=0)
            expected=self.s.pixel(rgb)
            self.s.set(skin_hue=140,skin_pick_on=1,skin_pick=(.70,.42,.175))
            self.assertRGB(self.s.pixel(rgb),expected)

    def test_range_picker_never_changes_normal_grade(self):
        self.s.set(look_mode=1)
        expected=self.s.pixel((.4,.12,.08))
        self.s.set(range_pick_on=1,range_pick=(0,0,1))
        self.assertRGB(self.s.pixel((.4,.12,.08)),expected)

    def test_guide_curve_matches_actual_pipeline(self):
        rng=random.Random(212)
        for _ in range(50):
            self.s.set(exposure=rng.uniform(-2,2),warm=rng.uniform(-.5,.5),tint=rng.uniform(-.5,.5),
                printer_r=rng.uniform(-2,2),printer_g=rng.uniform(-2,2),printer_b=rng.uniform(-2,2),
                negative_on=rng.randrange(2),print_on=rng.randrange(2),look_mode=rng.randrange(3),
                neg_contrast=rng.uniform(.5,2),print_density=rng.uniform(-.2,.2),
                skin_pick_on=rng.randrange(2),skin_pick=(.7,.42,.175))
            gray=.18*2**rng.uniform(-8,8)
            self.assertRGB(self.s.guide(gray),self.s.pixel((gray,)*3))

    def test_all_guides_require_internal_output(self):
        for mode in range(1,6):
            self.s.set(guide_mode=mode,output_mode=0)
            warning=self.s.pixel((.18,)*3,x=16,y=16)
            decoded=tuple(self.s.scalar(0,v) for v in warning)
            self.assertRGB(self.s.vector(2,decoded),(1,0,.65),tol=1e-5)

    def test_guide_warning_is_not_disabled_by_legend(self):
        for mode in range(1,6):
            self.s.set(guide_mode=mode,guide_opacity=.25)
            self.assertRGB(self.s.pixel((.18,)*3,x=0,y=0),(1,.6,0))

    def test_guide_off_restores_pixels(self):
        rgb=(.18,.12,.08);normal=self.s.pixel(rgb)
        for mode in range(1,6):
            self.s.set(guide_mode=mode)
            self.s.pixel(rgb)
            self.s.set(guide_mode=0)
            self.assertRGB(self.s.pixel(rgb),normal)

    def test_guide_preserves_pixels_outside_panel(self):
        normal=self.s.pixel((.18,)*3,x=50,y=700)
        for mode in range(1,5):
            self.s.set(guide_mode=mode)
            self.assertRGB(self.s.pixel((.18,)*3,x=50,y=700),normal)

    def test_graphics_finite_for_shapes_and_modes(self):
        rng=random.Random(79)
        for w,h in [(320,160),(480,270),(640,360),(1920,1080),(720,1280),(3840,2160)]:
            for mode in range(1,6):
                self.s.set(guide_mode=mode)
                for _ in range(80):
                    out=self.s.pixel((.18,.12,.08),w=w,h=h,x=rng.randrange(w),y=rng.randrange(h))
                    self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in out),(w,h,mode,out))

    def test_graphical_parameters_change_guides(self):
        # Compare a grid within the panel, not just an arbitrary pixel outside it.
        coords=[(x,y) for x in range(360,620,13) for y in range(30,180,11)]
        for mode,first,second in [
            (1,{'exposure':0},{'exposure':2}),
            (2,{'ev_low':-2,'ev_high':2},{'ev_low':1,'ev_high':4}),
            (3,{'range_hue':20},{'range_hue':180}),
            (4,{'skin_hue':20},{'skin_hue':180})]:
            self.s.set(guide_mode=mode,**first)
            before=[self.s.pixel((.18,)*3,w=640,h=360,x=x,y=y) for x,y in coords]
            self.s.set(**second)
            after=[self.s.pixel((.18,)*3,w=640,h=360,x=x,y=y) for x,y in coords]
            self.assertNotEqual(before,after)

class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basic=Shader(ROOT/'src/YSEW_UI_Probe_A2.dctl',helpers=False)
        cls.color=Shader(ROOT/'src/YSEW_Color_Probe_A2.dctl',helpers=False)
    @classmethod
    def tearDownClass(cls):
        cls.basic.temp.cleanup();cls.color.temp.cleanup()
    def setUp(self):self.basic.reset();self.color.reset()
    def test_basic_slider_and_dropdown(self):
        self.basic.set(probe_view=1,probe_gain=2)
        for v in self.basic.pixel((.1,.2,.3)):self.assertAlmostEqual(v,.36,delta=1e-7)
    def test_basic_integer_steps(self):
        self.basic.set(probe_view=2,probe_steps=4)
        for x,expected in [(0,0),(100,1/3),(200,2/3),(399,1)]:
            self.assertAlmostEqual(self.basic.pixel((.2,)*3,w=400,x=x)[0],expected,delta=1e-7)
    def test_checkbox_is_identity(self):
        for probe in (self.basic,self.color):
            probe.set(probe_on=0)
            out=probe.pixel((.2,.3,.4))
            for a,b in zip(out,(.2,.3,.4)):self.assertAlmostEqual(a,b,delta=1e-7)
    def test_native_picker_binding(self):
        self.color.set(probe_color=(.1,.3,.9))
        out=self.color.pixel((0,0,0))
        for a,b in zip(out,(.1,.3,.9)):self.assertAlmostEqual(a,b,delta=1e-7)
    def test_color_probe_input_passthrough(self):
        self.color.set(probe_view=0)
        for a,b in zip(self.color.pixel((.1,.2,.3)),(.1,.2,.3)):self.assertAlmostEqual(a,b,delta=1e-7)

if __name__=='__main__':unittest.main(verbosity=2)
