"""M7 show-look and Rec709 mastering-QC tests."""
from __future__ import annotations
import json, math, random, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests')); sys.path.insert(0,str(ROOT/'tools'))
from native import Shader
from ui_schema import parse_ui
from build import SOURCE

class M7DctlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.s=Shader()
    @classmethod
    def tearDownClass(cls): cls.s.temp.cleanup()
    def setUp(self):
        self.s.reset()
        self.s.set(input_mode=1,output_mode=2,wb_mode=2,negative_on=0,print_on=0,vignette_stops=0,
                   optics_on=0,texture_on=0,diag_mode=0,guide_mode=0,optics_view=0,texture_view=0,diag_legend=0)
    def close(self,a,b,tol=3e-5):
        for x,y in zip(a,b): self.assertTrue(math.isclose(x,y,rel_tol=tol,abs_tol=tol),(a,b))

    def test_m6_ui_prefix_frozen(self):
        old=json.loads((ROOT/'tests/ui_m6_compat.json').read_text()); cur=parse_ui(SOURCE.read_text())
        self.assertEqual(len(old),120)
        for a,b in zip(old,cur):
            self.assertEqual(a['name'],b.name); self.assertEqual(a['kind'],b.kind)
            self.assertEqual(a['values'],list(b.values))
            self.assertEqual(a['enums'],list(b.enums)[:len(a['enums'])])
            self.assertEqual(a['choices'],list(b.choices)[:len(a['choices'])])

    def test_new_look_indices_append_after_existing(self):
        ui={c.name:c for c in parse_ui(SOURCE.read_text())}
        look=ui['look_mode']
        self.assertEqual(list(look.enums)[:3],['LOOK_NEUTRAL','LOOK_FALL','LOOK_WINTER'])
        self.assertEqual(list(look.enums)[3:],['LOOK_NIGHT','LOOK_EXT_DAY','LOOK_EXT_DUSK'])

    def test_new_looks_are_distinct(self):
        rgb=(.28,.12,.055); outs=[]
        for mode in [0,1,2,3,4,5]:
            self.s.set(look_mode=mode,look_mix=1,skin_protect=0)
            outs.append(self.s.pixel(rgb,y=200))
        rounded={tuple(round(v,6) for v in o) for o in outs}
        self.assertEqual(len(rounded),6)

    def test_night_is_cooler_and_less_saturated_than_exterior_day(self):
        rgb=(.28,.14,.07)
        self.s.set(look_mix=1,skin_protect=0,look_mode=3)
        night=self.s.pixel(rgb,y=200)
        self.s.set(look_mode=4)
        day=self.s.pixel(rgb,y=200)
        # Night should carry relatively more blue and less channel separation.
        self.assertGreater(night[2]/max(night[0],1e-8),day[2]/max(day[0],1e-8))
        self.assertLess(max(night)-min(night),max(day)-min(day))

    def test_dusk_has_stronger_cool_shadow_bias_than_day(self):
        rgb=(.06,.07,.08)
        self.s.set(look_mix=1,skin_protect=0,look_mode=5)
        dusk=self.s.pixel(rgb,y=200)
        self.s.set(look_mode=4)
        day=self.s.pixel(rgb,y=200)
        self.assertGreater(dusk[2]/max(dusk[0],1e-8),day[2]/max(day[0],1e-8))

    def test_skin_protection_reduces_show_look_change(self):
        # Warm chromatic candidate close to the default skin hue.
        rgb=self.s.vector(3,(.18,.09,.06))
        self.s.set(look_mode=5,look_mix=1,skin_protect=0)
        unprotected=self.s.pixel(rgb,y=200)
        self.s.set(skin_protect=1)
        protected=self.s.pixel(rgb,y=200)
        self.s.set(look_mode=0)
        neutral=self.s.pixel(rgb,y=200)
        du=sum(abs(a-b) for a,b in zip(unprotected,neutral))
        dp=sum(abs(a-b) for a,b in zip(protected,neutral))
        self.assertLess(dp,du)

    def test_qc_pre_gamut_red_for_outside(self):
        self.s.set(diag_mode=33,qc_margin=10,gamut_on=0)
        out=self.s.pixel((1,0,0),y=200)
        self.assertGreater(out[0],.9); self.assertLess(out[1],.2)

    def test_qc_master_green_for_neutral_midgray(self):
        self.s.set(diag_mode=35,qc_margin=10,qc_comp=50)
        out=self.s.pixel((.18,.18,.18),y=200)
        self.close(out,(.10,.72,.20))

    def test_qc_master_amber_when_compression_is_strong(self):
        self.s.set(input_mode=2,diag_mode=35,qc_margin=1,qc_comp=1,gamut_on=1,gamut_knee=.1)
        # In-gamut Rec709 scene color with enough chroma to exceed the low compression knee.
        out=self.s.pixel((.18,.09,.09),y=200)
        self.assertGreater(out[0],.9); self.assertGreater(out[1],.3)

    def test_qc_controls_do_not_change_normal_grade(self):
        rgb=(.23,.11,.05); base=self.s.pixel(rgb,y=200)
        self.s.set(qc_margin=100,qc_comp=500)
        self.close(self.s.pixel(rgb,y=200),base,tol=1e-6)

    def test_new_modes_are_finite_and_bounded(self):
        rng=random.Random(707)
        for mode in [33,34,35]:
            self.s.set(diag_mode=mode)
            for _ in range(120):
                self.s.set(qc_margin=rng.randrange(1,101),qc_comp=rng.randrange(1,501),gamut_on=rng.randrange(2))
                out=self.s.pixel(tuple(rng.uniform(-.2,24) for _ in range(3)),y=200)
                self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in out),(mode,out))

if __name__=="__main__": unittest.main(verbosity=2)
