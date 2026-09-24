"""M6 destination-gamut, color-volume and scene-calibration diagnostic tests."""
from __future__ import annotations
import json, math, random, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests')); sys.path.insert(0,str(ROOT/'tools'))
from native import Shader
from ui_schema import parse_ui
from build import SOURCE

class M6DiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.s=Shader()
    @classmethod
    def tearDownClass(cls): cls.s.temp.cleanup()
    def setUp(self):
        self.s.reset()
        self.s.set(input_mode=1,output_mode=2,negative_on=0,print_on=0,look_mode=0,
                   vignette_stops=0,optics_on=0,texture_on=0,guide_mode=0,optics_view=0,texture_view=0,
                   diag_legend=0,wb_mode=2)
    def close(self,a,b,tol=3e-5):
        for x,y in zip(a,b): self.assertTrue(math.isclose(x,y,rel_tol=tol,abs_tol=tol),(a,b))

    def test_m5_ui_prefix_frozen(self):
        old=json.loads((ROOT/'tests/ui_m5_compat.json').read_text()); cur=parse_ui(SOURCE.read_text())
        self.assertEqual(len(old),114)
        for a,b in zip(old,cur):
            self.assertEqual(a['name'],b.name); self.assertEqual(a['kind'],b.kind)
            self.assertEqual(a['values'],list(b.values)); self.assertEqual(a['enums'],list(b.enums)); self.assertEqual(a['choices'],list(b.choices))

    def test_p3d65_xyz_matrix_reference(self):
        self.close(self.s.vector(15,(1,0,0)),(2.493496911941425,-.829488969561575,.035845830243784))
        self.close(self.s.vector(15,(0,1,0)),(-.931383617919124,1.762664060318346,-.076172389268041))
        self.close(self.s.vector(15,(0,0,1)),(-.402710784450717,.023624685841944,.956884524007687))

    def test_rec2020_xyz_matrix_reference(self):
        self.close(self.s.vector(16,(1,0,0)),(1.716651187971268,-.666684351832489,.017639857445311))
        self.close(self.s.vector(16,(0,1,0)),(-.355670783776392,1.616481236634939,-.042770613257809))
        self.close(self.s.vector(16,(0,0,1)),(-.253366281373660,.015768545813911,.942103121235474))

    def test_all_targets_preserve_d65_neutral(self):
        for target in [0,1,2]:
            self.close(self.s.vector(17,(1,1,1),target),(1,1,1),tol=4e-5)

    def test_neutral_render_matches_output_gray_in_all_targets(self):
        expected=.42**2.4
        for target in [0,1,2]:
            out=self.s.vector(18,(.18,.18,.18),target,.42)
            self.close(out,(expected,)*3,tol=4e-5)

    def test_occupancy_and_headroom_geometry(self):
        self.assertAlmostEqual(self.s.scalar(16,.5,.5,.5,0),0,delta=1e-6)
        self.assertAlmostEqual(self.s.scalar(16,1,0,0,0),1,delta=1e-6)
        self.assertAlmostEqual(self.s.scalar(17,.5,.5,.5),.5,delta=1e-6)
        self.assertAlmostEqual(self.s.scalar(17,1,0,0),0,delta=1e-6)
        self.assertLess(self.s.scalar(17,1.1,.2,.2),0)

    def test_calibration_profile_targets(self):
        self.assertAlmostEqual(self.s.scalar(18,0,999),.18,delta=1e-7)
        self.assertAlmostEqual(self.s.scalar(18,1,999),.90,delta=1e-7)
        self.assertAlmostEqual(self.s.scalar(18,2,999),.02,delta=1e-7)
        self.assertAlmostEqual(self.s.scalar(18,3,250),.25,delta=1e-7)

    def test_neutral_xy_error_is_zero_for_d65_neutral(self):
        self.assertLess(self.s.scalar(19,.18,.18,.18),2e-5)
        self.assertGreater(self.s.scalar(19,.30,.10,.05),.01)

    def test_p3_red_is_outside_709_but_on_p3_boundary(self):
        p3_red_xyz=(.486570948648216,.228974564069749,0)
        dwg=self.s.vector(1,p3_red_xyz)
        self.s.set(diag_mode=27,diag_gamut=0,gamut_margin=20)
        a=self.s.pixel(dwg,y=200)
        self.close(a,(1,.05,.10),tol=3e-5)
        self.s.set(diag_gamut=1)
        b=self.s.pixel(dwg,y=200)
        self.close(b,(1,.75,0),tol=3e-5)

    def test_2020_green_is_outside_p3_but_on_2020_boundary(self):
        xyz=(.144616903586208,.677998071518871,.028072693049087)
        dwg=self.s.vector(1,xyz)
        self.s.set(diag_mode=27,diag_gamut=1,gamut_margin=20)
        self.close(self.s.pixel(dwg,y=200),(1,.05,.10),tol=3e-5)
        self.s.set(diag_gamut=2)
        self.close(self.s.pixel(dwg,y=200),(1,.75,0),tol=3e-5)

    def test_cal_exposure_exact_under_over(self):
        self.s.set(diag_mode=30,cal_profile=0,cal_tol=15)
        exact=self.s.pixel((.18,.18,.18),y=200)
        self.close(exact,(.10,.75,.20))
        under=self.s.pixel((.09,.09,.09),y=200)
        over=self.s.pixel((.36,.36,.36),y=200)
        self.assertGreater(under[2],under[0])
        self.assertGreater(over[0],over[2])

    def test_cal_neutral_exact_and_tinted(self):
        self.s.set(diag_mode=31,cal_neutral=10)
        self.close(self.s.pixel((.18,.18,.18),y=200),(.10,.75,.20))
        tinted=self.s.pixel((.30,.10,.05),y=200)
        self.assertGreater(tinted[0],tinted[1])

    def test_cal_combined_good_and_bad(self):
        self.s.set(diag_mode=32,cal_profile=0,cal_tol=15,cal_neutral=10)
        self.close(self.s.pixel((.18,.18,.18),y=200),(.10,.75,.20))
        bad=self.s.pixel((.45,.08,.02),y=200)
        self.assertGreater(bad[0],.8)

    def test_m6_controls_do_not_change_normal_grade(self):
        self.s.set(diag_mode=0)
        rgb=(.23,.11,.05); base=self.s.pixel(rgb,y=200)
        self.s.set(diag_gamut=2,gamut_margin=200,cal_profile=3,cal_target=3500,cal_tol=200,cal_neutral=200)
        self.close(self.s.pixel(rgb,y=200),base,tol=1e-6)

    def test_new_diagnostics_finite_bounded(self):
        rng=random.Random(606)
        for mode in range(27,33):
            self.s.set(diag_mode=mode)
            for _ in range(100):
                self.s.set(diag_gamut=rng.randrange(3),gamut_margin=rng.randrange(1,251),
                           cal_profile=rng.randrange(4),cal_target=rng.randrange(1,4001),
                           cal_tol=rng.randrange(1,201),cal_neutral=rng.randrange(1,201))
                out=self.s.pixel(tuple(rng.uniform(-.2,24) for _ in range(3)),y=200)
                self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in out),(mode,out))

if __name__=="__main__": unittest.main(verbosity=2)
