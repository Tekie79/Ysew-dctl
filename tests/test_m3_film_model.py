"""M3 advanced parametric negative/print behavior and compatibility tests."""
from __future__ import annotations
import json, math, random, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))
from native import Shader
from ui_schema import parse_ui
from build import SOURCE

class M3FilmModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.s=Shader()
    @classmethod
    def tearDownClass(cls): cls.s.temp.cleanup()
    def setUp(self):
        self.s.reset()
        self.s.set(input_mode=1,output_mode=1,wb_mode=2,look_mode=0,vignette_stops=0)
    def assertRGB(self,a,b,tol=4e-6):
        for aa,bb in zip(a,b):
            self.assertTrue(math.isclose(aa,bb,rel_tol=tol,abs_tol=tol),(a,b))

    def test_m2_ui_contract_prefix_is_unchanged(self):
        old=json.loads((ROOT/'tests/ui_m2_compat.json').read_text())
        current=parse_ui(SOURCE.read_text())
        self.assertEqual(len(old),67)
        for before,after in zip(old,current):
            self.assertEqual(before['name'],after.name)
            self.assertEqual(before['kind'],after.kind)
            self.assertEqual(before['values'],list(after.values))
            self.assertEqual(before['enums'],list(after.enums))
            self.assertEqual(before['choices'],list(after.choices))

    def test_legacy_is_default_and_new_controls_are_inert(self):
        self.s.reset()
        rgb=(.32,.11,.045)
        baseline=self.s.pixel(rgb)
        self.s.set(adv_neg_density=.3,adv_neg_color=0,adv_neg_sep=1,adv_neg_shadow=0,
                   adv_neg_high=0,adv_neg_warm=1,adv_neg_green=-1,adv_neg_cool=1,
                   adv_print_black=1,adv_print_white=-1,adv_print_sep=1,
                   adv_print_warm=1,adv_print_color=0)
        self.assertRGB(self.s.pixel(rgb),baseline,tol=1e-5)

    def test_advanced_model_changes_color_image(self):
        rgb=(.35,.12,.045)
        legacy=self.s.pixel(rgb)
        self.s.set(film_model=1)
        advanced=self.s.pixel(rgb)
        self.assertGreater(sum(abs(a-b) for a,b in zip(legacy,advanced)),1e-4)

    def test_negative_and_print_bypasses_still_work(self):
        rgb=(.3,.12,.05)
        self.s.set(film_model=1,negative_on=0,print_on=0)
        self.assertRGB(self.s.pixel(rgb),rgb)
        self.s.set(negative_on=1)
        self.assertNotEqual(self.s.pixel(rgb),rgb)
        self.s.set(negative_on=0,print_on=1)
        self.assertNotEqual(self.s.pixel(rgb),rgb)

    def test_negative_density_is_neutral_base10_trim_when_other_advanced_color_is_neutralized(self):
        self.s.set(film_model=1,print_on=0,neg_contrast=1,neg_toe=0,neg_shoulder=0,
                   neg_sat=1,crosstalk=0,adv_neg_sep=0,adv_neg_color=1,
                   adv_neg_shadow=1,adv_neg_high=1,adv_neg_warm=0,adv_neg_green=0,adv_neg_cool=0)
        rgb=(.18,.18,.18)
        self.s.set(adv_neg_density=.2)
        expected=.18*10**(-.2)
        self.assertRGB(self.s.pixel(rgb),(expected,)*3,tol=2e-5)

    def test_density_separation_preserves_neutral(self):
        self.s.set(film_model=1,print_on=0,neg_contrast=1,neg_toe=0,neg_shoulder=0,
                   neg_sat=1,crosstalk=0,adv_neg_density=0,adv_neg_color=1,
                   adv_neg_shadow=1,adv_neg_high=1,adv_neg_warm=0,adv_neg_green=0,adv_neg_cool=0)
        for sep in [0,.25,.5,1]:
            self.s.set(adv_neg_sep=sep)
            self.assertRGB(self.s.pixel((.18,.18,.18)),(.18,.18,.18),tol=2e-5)

    def test_density_separation_increases_channel_separation_on_positive_color(self):
        self.s.set(film_model=1,print_on=0,neg_contrast=1,neg_toe=0,neg_shoulder=0,
                   neg_sat=1,crosstalk=0,adv_neg_density=0,adv_neg_color=1,
                   adv_neg_shadow=1,adv_neg_high=1,adv_neg_warm=0,adv_neg_green=0,adv_neg_cool=0)
        rgb=(.28,.16,.09)
        self.s.set(adv_neg_sep=0); a=self.s.pixel(rgb)
        self.s.set(adv_neg_sep=1); b=self.s.pixel(rgb)
        self.assertGreater(max(b)-min(b),max(a)-min(a))

    def test_shadow_and_highlight_chroma_controls_are_exposure_selective(self):
        base=(.36,.18,.09)
        self.s.set(film_model=1,print_on=0,neg_contrast=1,neg_toe=0,neg_shoulder=0,
                   neg_sat=1,crosstalk=0,adv_neg_density=0,adv_neg_color=1,adv_neg_sep=0,
                   adv_neg_warm=0,adv_neg_green=0,adv_neg_cool=0)
        def chroma(rgb): return max(rgb)-min(rgb)
        self.s.set(adv_neg_shadow=0,adv_neg_high=1)
        dark=self.s.pixel(tuple(v*.03 for v in base)); bright=self.s.pixel(tuple(v*12 for v in base))
        self.s.set(adv_neg_shadow=1,adv_neg_high=1)
        dark_full=self.s.pixel(tuple(v*.03 for v in base)); bright_full=self.s.pixel(tuple(v*12 for v in base))
        self.assertLess(chroma(dark),chroma(dark_full)*.45)
        self.assertTrue(math.isclose(chroma(bright),chroma(bright_full),rel_tol=.03))
        self.s.set(adv_neg_shadow=1,adv_neg_high=0)
        bright_low=self.s.pixel(tuple(v*12 for v in base))
        self.assertLess(chroma(bright_low),chroma(bright_full)*.55)

    def test_hue_biases_are_selective_and_luminance_stable(self):
        self.s.set(film_model=1,print_on=0,neg_contrast=1,neg_toe=0,neg_shoulder=0,
                   neg_sat=1,crosstalk=0,adv_neg_density=0,adv_neg_color=1,
                   adv_neg_sep=0,adv_neg_shadow=1,adv_neg_high=1)
        warm=(.30,.13,.06); cool=(.06,.13,.30)
        self.s.set(adv_neg_warm=0,adv_neg_green=0,adv_neg_cool=0)
        w0=self.s.pixel(warm); c0=self.s.pixel(cool)
        self.s.set(adv_neg_warm=1)
        w1=self.s.pixel(warm); c1=self.s.pixel(cool)
        self.assertGreater(sum(abs(a-b) for a,b in zip(w0,w1)),sum(abs(a-b) for a,b in zip(c0,c1))*1.8)
        yw=lambda x: .27411851*x[0]+.87363190*x[1]-.14775041*x[2]
        self.assertAlmostEqual(yw(w0),yw(w1),delta=3e-5)

    def test_print_black_and_white_are_region_selective(self):
        self.s.set(film_model=1,negative_on=0,print_on=1,print_contrast=1,print_toe=0,
                   print_shoulder=0,print_density=0,print_sat=1,adv_print_sep=0,
                   adv_print_warm=0,adv_print_color=1)
        dark=(.018,)*3; bright=(1.8,)*3
        self.s.set(adv_print_black=1,adv_print_white=0)
        d1=self.s.pixel(dark)[0]; b1=self.s.pixel(bright)[0]
        self.s.set(adv_print_black=0,adv_print_white=0)
        d0=self.s.pixel(dark)[0]; b0=self.s.pixel(bright)[0]
        self.assertLess(d1,d0*.7)
        self.assertTrue(math.isclose(b1,b0,rel_tol=.02))
        self.s.set(adv_print_white=1)
        self.assertGreater(self.s.pixel(bright)[0],b0*1.4)

    def test_advanced_neutral_ramp_is_monotonic(self):
        self.s.set(film_model=1,look_mode=0)
        values=[]
        for i in range(-96,97):
            x=.18*2**(i/12)
            values.append(self.s.pixel((x,x,x))[0])
        self.assertTrue(all(a<b for a,b in zip(values,values[1:])))

    def test_tone_guide_matches_advanced_pipeline(self):
        self.s.set(output_mode=2,film_model=1,adv_neg_sep=.55,adv_neg_warm=.3,adv_print_black=.2,
                   adv_print_white=.15,adv_print_sep=.35,adv_print_warm=.2)
        for gray in [.018,.09,.18,.72,2.88]:
            self.assertRGB(self.s.guide(gray),self.s.pixel((gray,gray,gray)),tol=2e-5)

    def test_randomized_advanced_controls_remain_finite(self):
        rng=random.Random(303)
        self.s.set(film_model=1)
        for _ in range(600):
            self.s.set(
                adv_neg_density=rng.uniform(-.3,.3),adv_neg_color=rng.uniform(0,1.5),
                adv_neg_sep=rng.random(),adv_neg_shadow=rng.uniform(0,1.25),
                adv_neg_high=rng.uniform(0,1.25),adv_neg_warm=rng.uniform(-1,1),
                adv_neg_green=rng.uniform(-1,1),adv_neg_cool=rng.uniform(-1,1),
                adv_print_black=rng.uniform(-1,1),adv_print_white=rng.uniform(-1,1),
                adv_print_sep=rng.random(),adv_print_warm=rng.uniform(-1,1),
                adv_print_color=rng.uniform(0,1.5))
            out=self.s.pixel(tuple(rng.uniform(-.2,32) for _ in range(3)))
            self.assertTrue(all(math.isfinite(v) for v in out),out)

if __name__=="__main__": unittest.main(verbosity=2)
