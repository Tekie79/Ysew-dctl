"""M5 temporal grain, density response, lens softness and compatibility tests."""
from __future__ import annotations
import json, math, random, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests')); sys.path.insert(0,str(ROOT/'tools'))
from native import Shader
from ui_schema import parse_ui
from build import SOURCE

def pix(img,w,x,y):
    i=3*(y*w+x); return img[i:i+3]

class M5TextureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.s=Shader()
    @classmethod
    def tearDownClass(cls): cls.s.temp.cleanup()
    def setUp(self):
        self.s.reset()
        self.s.set(input_mode=1,output_mode=1,wb_mode=2,negative_on=0,print_on=0,look_mode=0,
            vignette_stops=0,optics_on=0,diag_mode=0,guide_mode=0,optics_view=0,texture_view=0)
    def close(self,a,b,tol=5e-6):
        for x,y in zip(a,b): self.assertTrue(math.isclose(x,y,rel_tol=tol,abs_tol=tol),(a,b))

    def test_m4_ui_prefix_frozen(self):
        old=json.loads((ROOT/'tests/ui_m4_compat.json').read_text()); cur={c.name:c for c in parse_ui(SOURCE.read_text())}
        self.assertEqual(len(old),99)
        for a in old:
            b=cur[a['name']]
            self.assertEqual(a['kind'],b.kind)
            self.assertEqual(a['values'],list(b.values)); self.assertEqual(a['enums'],list(b.enums)[:len(a['enums'])]); self.assertEqual(a['choices'],list(b.choices)[:len(a['choices'])])

    def test_texture_off_is_exact_compatibility(self):
        rgb=(.31,.14,.06); base=self.s.pixel(rgb,w=128,h=72,x=37,y=29)
        self.s.set(grain_amount=200,grain_size=300,grain_rough=100,grain_color=100,grain_shadow=200,grain_mid=200,
                   grain_high=200,lens_soft=100,lens_radius=24,micro_soft=100)
        self.close(self.s.pixel(rgb,w=128,h=72,x=37,y=29),base)

    def test_zero_amounts_are_inert(self):
        rgb=(.31,.14,.06); base=self.s.pixel(rgb,w=128,h=72,x=37,y=29)
        self.s.set(texture_on=1,grain_amount=0,lens_soft=0,micro_soft=0,grain_seed=9999)
        self.close(self.s.pixel(rgb,w=128,h=72,x=37,y=29),base)

    def test_same_frame_seed_is_deterministic(self):
        self.s.set(texture_on=1,grain_amount=100,grain_motion=1,grain_seed=1234)
        self.s.set_frame(17); a=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.s.set_frame(17); b=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.assertEqual(a,b)

    def test_every_frame_changes_grain(self):
        self.s.set(texture_on=1,grain_amount=100,grain_motion=1,grain_seed=1234)
        self.s.set_frame(17); a=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.s.set_frame(18); b=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.assertGreater(sum(abs(x-y) for x,y in zip(a,b)),1e-6)

    def test_static_ignores_frame(self):
        self.s.set(texture_on=1,grain_amount=100,grain_motion=0,grain_seed=1234)
        self.s.set_frame(1); a=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.s.set_frame(900); b=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.assertEqual(a,b)

    def test_hold2(self):
        self.s.set(texture_on=1,grain_amount=100,grain_motion=2,grain_seed=987)
        self.s.set_frame(10); a=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.s.set_frame(11); b=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.s.set_frame(12); c=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.assertEqual(a,b); self.assertNotEqual(b,c)

    def test_seed_changes_pattern(self):
        self.s.set(texture_on=1,grain_amount=100,grain_motion=0,grain_seed=1)
        a=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.s.set(grain_seed=2); b=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.assertNotEqual(a,b)

    def test_monochrome_grain_keeps_neutral_equal(self):
        self.s.set(texture_on=1,grain_amount=100,grain_color=0,grain_motion=0)
        r,g,b=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.assertAlmostEqual(r,g,delta=2e-7); self.assertAlmostEqual(g,b,delta=2e-7)

    def test_color_grain_separates_neutral(self):
        self.s.set(texture_on=1,grain_amount=150,grain_color=100,grain_motion=0)
        out=self.s.pixel((.18,.18,.18),w=1920,h=1080,x=431,y=217)
        self.assertGreater(max(out)-min(out),1e-5)

    def test_exposure_weight_suppression(self):
        self.s.set(texture_on=1,grain_amount=150,grain_color=0,grain_motion=0,grain_shadow=0,grain_mid=100,grain_high=0)
        dark=.18*2**-6; mid=.18; high=.18*2**7
        self.close(self.s.pixel((dark,)*3,w=1920,h=1080,x=431,y=217),(dark,)*3,tol=2e-6)
        self.assertGreater(abs(self.s.pixel((mid,)*3,w=1920,h=1080,x=431,y=217)[0]-mid),1e-6)
        self.close(self.s.pixel((high,)*3,w=1920,h=1080,x=431,y=217),(high,)*3,tol=2e-5)

    def test_resolution_normalized_coordinates(self):
        self.s.set(texture_on=1,grain_amount=100,grain_motion=0,grain_color=0,grain_gauge=2,grain_size=100)
        self.close(self.s.pixel((.18,)*3,w=64,h=64,x=16,y=16),
                   self.s.pixel((.18,)*3,w=128,h=128,x=32,y=32),tol=2e-6)

    def test_gauge_and_size_change_pattern(self):
        self.s.set(texture_on=1,grain_amount=100,grain_motion=0,grain_color=0,grain_gauge=0,grain_size=100)
        a=self.s.pixel((.18,)*3,w=1920,h=1080,x=431,y=217)
        self.s.set(grain_gauge=3); b=self.s.pixel((.18,)*3,w=1920,h=1080,x=431,y=217)
        self.s.set(grain_gauge=2,grain_size=250); c=self.s.pixel((.18,)*3,w=1920,h=1080,x=431,y=217)
        self.assertNotEqual(a,b); self.assertNotEqual(b,c)

    def test_lens_soft_spreads_impulse(self):
        w=h=65; data=[0.0]*(w*h*3); i=(32*w+32)*3; data[i:i+3]=[2,2,2]
        base=self.s.render_image(data,w,h)
        self.s.set(texture_on=1,lens_soft=100,lens_radius=24)
        out=self.s.render_image(data,w,h)
        self.assertLess(sum(pix(out,w,32,32)),sum(pix(base,w,32,32)))
        self.assertGreater(sum(pix(out,w,33,32)),sum(pix(base,w,33,32)))

    def test_micro_soft_reduces_impulse(self):
        w=h=65; data=[.18]*(w*h*3); i=(32*w+32)*3; data[i:i+3]=[1.8,1.8,1.8]
        base=self.s.render_image(data,w,h)
        self.s.set(texture_on=1,micro_soft=100,lens_radius=24)
        out=self.s.render_image(data,w,h)
        self.assertLess(sum(pix(out,w,32,32)),sum(pix(base,w,32,32)))

    def test_texture_view_guard(self):
        self.s.set(texture_on=1,grain_amount=100,texture_view=1,output_mode=1)
        warn=self.s.pixel((.18,)*3,w=64,h=64,x=16,y=16)
        self.s.set(texture_view=0); normal=self.s.pixel((.18,)*3,w=64,h=64,x=16,y=16)
        self.assertGreater(sum(abs(a-b) for a,b in zip(warn,normal)),.1)

    def test_randomized_finite(self):
        rng=random.Random(505); self.s.set(texture_on=1)
        for _ in range(350):
            self.s.set(grain_amount=rng.randrange(201),grain_size=rng.randrange(50,301),grain_rough=rng.randrange(101),
                grain_color=rng.randrange(101),grain_shadow=rng.randrange(201),grain_mid=rng.randrange(201),
                grain_high=rng.randrange(201),grain_gauge=rng.randrange(5),grain_motion=rng.randrange(4),
                grain_seed=rng.randrange(10000),lens_soft=rng.randrange(101),lens_radius=rng.randrange(1,25),
                micro_soft=rng.randrange(101))
            self.s.set_frame(rng.randrange(10000))
            out=self.s.pixel(tuple(rng.uniform(-.1,16) for _ in range(3)),w=320,h=180,x=rng.randrange(320),y=rng.randrange(180))
            self.assertTrue(all(math.isfinite(v) for v in out),out)

if __name__=="__main__": unittest.main(verbosity=2)
