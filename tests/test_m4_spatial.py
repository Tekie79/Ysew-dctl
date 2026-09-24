"""M4 spatial optics tests through the CPU texture adapter."""
from __future__ import annotations
import json, math, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests')); sys.path.insert(0,str(ROOT/'tools'))
from native import Shader
from ui_schema import parse_ui
from build import SOURCE

def pix(img,w,x,y):
    i=3*(y*w+x); return img[i:i+3]

class M4SpatialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.s=Shader()
    @classmethod
    def tearDownClass(cls): cls.s.temp.cleanup()
    def setUp(self):
        self.s.reset(); self.s.set(input_mode=1,output_mode=1,wb_mode=2,negative_on=0,
            print_on=0,look_mode=0,vignette_stops=0,diag_mode=0,guide_mode=0,optics_view=0)
    def close(self,a,b,tol=5e-6):
        for x,y in zip(a,b): self.assertTrue(math.isclose(x,y,rel_tol=tol,abs_tol=tol),(a,b))
    def test_m3_ui_prefix_frozen(self):
        old=json.loads((ROOT/'tests/ui_m3_compat.json').read_text()); cur=parse_ui(SOURCE.read_text())
        self.assertEqual(len(old),81)
        for a,b in zip(old,cur):
            self.assertEqual(a['name'],b.name); self.assertEqual(a['kind'],b.kind)
            self.assertEqual(a['values'],list(b.values)); self.assertEqual(a['enums'],list(b.enums)); self.assertEqual(a['choices'],list(b.choices))
    def test_optics_off_is_exact_compatibility(self):
        rgb=(.31,.14,.06); base=self.s.pixel(rgb,w=97,h=55,x=48,y=27)
        self.s.set(optics_quality=2,optics_mix=2,halation_amount=2,bloom_amount=2,glow_amount=2,veil_amount=1,halation_tint=1)
        self.close(self.s.pixel(rgb,w=97,h=55,x=48,y=27),base)
    def test_constant_field_has_no_spread(self):
        w=h=33; data=[2.0,1.4,1.0]*(w*h); base=self.s.render_image(data,w,h)
        self.s.set(optics_on=1,halation_amount=1,bloom_amount=1,glow_amount=1,veil_amount=.8,
            halation_threshold=-2,bloom_threshold=-2,glow_threshold=-2,veil_threshold=-2)
        out=self.s.render_image(data,w,h)
        for a,b in zip(out,base): self.assertTrue(math.isclose(a,b,rel_tol=2e-5,abs_tol=2e-5))
    def test_impulse_spreads(self):
        w=h=65; data=[0.0]*(w*h*3); i=(32*w+32)*3; data[i:i+3]=[16,12,8]
        base=self.s.render_image(data,w,h)
        self.s.set(optics_on=1,optics_quality=1,bloom_amount=1,bloom_radius=36,bloom_threshold=-2,optics_soft=.5)
        out=self.s.render_image(data,w,h)
        self.assertGreater(sum(pix(out,w,33,32)),sum(pix(base,w,33,32))+1e-5)
    def test_halation_is_red_orange(self):
        w=h=65; data=[0.0]*(w*h*3); i=(32*w+32)*3; data[i:i+3]=[20,20,20]
        self.s.set(optics_on=1,optics_quality=1,halation_amount=1,halation_radius=30,halation_threshold=-2,halation_tint=.35)
        r,g,b=pix(self.s.render_image(data,w,h),w,34,32)
        self.assertGreater(r,g); self.assertGreater(g,b)
    def test_halation_tint_increases_green(self):
        w=h=65; data=[0.0]*(w*h*3); i=(32*w+32)*3; data[i:i+3]=[20,20,20]
        self.s.set(optics_on=1,optics_quality=1,halation_amount=1,halation_radius=30,halation_threshold=-2,halation_tint=0)
        a=self.s.render_image(data,w,h); self.s.set(halation_tint=1); b=self.s.render_image(data,w,h)
        self.assertGreater(pix(b,w,34,32)[1],pix(a,w,34,32)[1])
    def test_high_threshold_rejects_gray_impulse(self):
        w=h=49; data=[0.0]*(w*h*3); i=(24*w+24)*3; data[i:i+3]=[.18,.18,.18]
        self.s.set(optics_on=1,bloom_amount=1,bloom_radius=24,bloom_threshold=6,optics_soft=.1)
        a=self.s.render_image(data,w,h); self.s.set(optics_on=0); b=self.s.render_image(data,w,h)
        for x,y in zip(a,b): self.assertTrue(math.isclose(x,y,abs_tol=2e-6))
    def test_quality_tiers_deterministic_finite(self):
        w=h=35; data=[]
        for y in range(h):
            for x in range(w):
                v=8.0 if (x-17)**2+(y-17)**2<9 else .02; data += [v,v*.8,v*.6]
        for q in [0,1,2]:
            self.s.set(optics_on=1,optics_quality=q,bloom_amount=.7,glow_amount=.4,halation_amount=.5,veil_amount=.15,
                bloom_threshold=-1,glow_threshold=-1,halation_threshold=-1,veil_threshold=-1)
            a=self.s.render_image(data,w,h); b=self.s.render_image(data,w,h)
            self.assertEqual(a,b); self.assertTrue(all(math.isfinite(v) for v in a))
    def test_zero_amount_path_matches_optics_off(self):
        w=h=27; data=[]
        for y in range(h):
            for x in range(w):
                v=(x+y)/(w+h); data += [v,v*.8,v*.6]
        self.s.set(optics_on=1,optics_quality=2,optics_mix=2,optics_soft=2,halation_radius=110,bloom_radius=170,glow_radius=290,veil_radius=580)
        a=self.s.render_image(data,w,h); self.s.set(optics_on=0); b=self.s.render_image(data,w,h)
        for x,y in zip(a,b): self.assertTrue(math.isclose(x,y,rel_tol=2e-6,abs_tol=2e-6))
    def test_contribution_view_guard(self):
        self.s.set(optics_on=1,bloom_amount=1,optics_view=2,output_mode=1)
        warn=self.s.pixel((4,4,4),w=64,h=64,x=16,y=16)
        self.s.set(optics_view=0); normal=self.s.pixel((4,4,4),w=64,h=64,x=16,y=16)
        self.assertGreater(sum(abs(a-b) for a,b in zip(warn,normal)),.1)

if __name__=="__main__": unittest.main(verbosity=2)
