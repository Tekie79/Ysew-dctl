"""M2 technical input science and CAT02 white-balance tests."""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from native import Shader

class M2InputScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.s=Shader()
    @classmethod
    def tearDownClass(cls): cls.s.temp.cleanup()
    def setUp(self):
        self.s.reset()
        self.s.set(negative_on=0,print_on=0,look_mode=0,vignette_stops=0,
                   output_mode=1,wb_mode=2,warm=0,tint=0)
    def assertRGB(self,a,b,tol=2e-5):
        for aa,bb in zip(a,b):
            self.assertTrue(math.isclose(aa,bb,rel_tol=tol,abs_tol=tol),(a,b))

    def test_arri_logc4_published_gray_references(self):
        self.assertAlmostEqual(self.s.scalar(10,0.0929),0.0,delta=2e-4)
        self.assertAlmostEqual(self.s.scalar(10,0.2784),0.18,delta=3e-4)
    def test_arri_logc4_signed_roundtrip(self):
        for v in [-.02,-.01,0,.001,.18,1,8,64]:
            self.assertAlmostEqual(self.s.scalar(10,self.s.scalar(13,v)),v,delta=max(1e-6,abs(v)*2e-6))
    def test_arri_awg4_xyz_published_matrix(self):
        self.assertRGB(self.s.vector(8,(1,0,0)),(.704858320407232,.254524176404027,0))
        self.assertRGB(self.s.vector(8,(0,1,0)),(.129760295170463,.781477732712002,0))
        self.assertRGB(self.s.vector(8,(0,0,1)),(.115837311473977,-.036001909116029,1.089057750759878))

    def test_slog3_published_code_values(self):
        self.assertAlmostEqual(self.s.scalar(11,95/1023),0.0,delta=2e-6)
        self.assertAlmostEqual(self.s.scalar(11,420/1023),0.18,delta=2e-6)
        self.assertAlmostEqual(self.s.scalar(11,598/1023),0.9,delta=3e-3)
    def test_slog3_roundtrip(self):
        for v in [-.005,0,.001,.01125,.18,.9,1,8]:
            self.assertAlmostEqual(self.s.scalar(11,self.s.scalar(14,v)),v,delta=max(2e-6,abs(v)*3e-6))
    def test_sgamut3cine_matrix_from_published_primaries(self):
        self.assertRGB(self.s.vector(9,(1,0,0)),(.599083920758672,.215075820116077,-.032065849545822))
        self.assertRGB(self.s.vector(9,(0,1,0)),(.248925516115147,.885068501744598,-.027658390679458))
        self.assertRGB(self.s.vector(9,(0,0,1)),(.102446490178174,-.100144321860675,1.148781990204675))
    def test_sgamut3_matrix_from_published_primaries(self):
        self.assertRGB(self.s.vector(10,(1,0,0)),(.706482713192173,.270979670813193,-.009677845386151))
        self.assertRGB(self.s.vector(10,(0,1,0)),(.128801049791290,.786606411201264,.004600037492436))
        self.assertRGB(self.s.vector(10,(0,0,1)),(.115172164759678,-.057586082014457,1.094135555285109))

    def test_red_log3g10_published_mapping(self):
        for code,linear,tol in [(0,-.01,2e-6),(.091551,0,3e-6),(.333333,.18,3e-6),(.493449,1,1e-5),(1,184.322,2e-2)]:
            self.assertAlmostEqual(self.s.scalar(12,code),linear,delta=tol)
    def test_red_log3g10_roundtrip(self):
        for v in [-.02,-.01,0,.18,1,16,184.32]:
            self.assertAlmostEqual(self.s.scalar(12,self.s.scalar(15,v)),v,delta=max(3e-6,abs(v)*3e-6))
    def test_red_rwg_xyz_published_matrix(self):
        self.assertRGB(self.s.vector(11,(1,0,0)),(.735275,.286694,-.079681))
        self.assertRGB(self.s.vector(11,(0,1,0)),(.068609,.842979,-.347343))
        self.assertRGB(self.s.vector(11,(0,0,1)),(.146571,-.129673,1.516081))

    def test_camera_input_neutral_18_percent(self):
        for mode,code,tol in [(3,.2784,5e-4),(4,420/1023,5e-5),(5,420/1023,5e-5),(6,.333333,5e-5)]:
            self.s.set(input_mode=mode)
            self.assertRGB(self.s.pixel((code,code,code)),(.18,.18,.18),tol=tol)
    def test_camera_spaces_preserve_d65_neutral(self):
        for op in [8,9,10,11]:
            self.assertRGB(self.s.vector(op,(1,1,1)),(.950455927051672,1,1.089057750759878),tol=2e-5)

    def test_cct_6504_is_near_d65(self):
        xy=self.s.vector(14,(0,0,0),6504)
        self.assertAlmostEqual(xy[0],.312714,delta=3e-4)
        self.assertAlmostEqual(xy[1],.329119,delta=3e-4)
    def test_cat02_d65_identity(self):
        for rgb in [(.18,.18,.18),(.3,.12,.04),(-.01,.05,.9)]:
            self.assertRGB(self.s.vector(12,rgb,6504,0),rgb,tol=2e-5)
    def test_cat02_maps_source_white_to_d65(self):
        xy=self.s.vector(14,(0,0,0),3200)
        src_xyz=(xy[0]/xy[1],1,(1-xy[0]-xy[1])/xy[1])
        src_dwg=self.s.vector(1,src_xyz)
        xyz=self.s.vector(0,self.s.vector(12,src_dwg,3200,0))
        self.assertRGB(xyz,(.950455927051672,1,1.089057750759878),tol=8e-5)
    def test_cat02_strength_zero_is_identity(self):
        self.s.set(input_mode=1,wb_mode=1,wb_temp=3200,wb_duv=.01,wb_strength=0)
        self.assertRGB(self.s.pixel((.18,.12,.08)),(.18,.12,.08))
    def test_wb_off_ignores_legacy_warmth_and_tint(self):
        self.s.set(input_mode=1,wb_mode=2,warm=1,tint=-1)
        a=self.s.pixel((.18,.12,.08))
        self.s.set(warm=0,tint=0)
        self.assertRGB(a,self.s.pixel((.18,.12,.08)))
    def test_legacy_default_remains_alpha_behavior(self):
        self.s.reset(); self.s.set(input_mode=1,negative_on=0,print_on=0,look_mode=0,vignette_stops=0,output_mode=1,warm=.4,tint=-.2)
        before=self.s.pixel((.18,.12,.08))
        self.s.set(wb_mode=0,wb_temp=3200,wb_duv=.03,wb_strength=.2)
        self.assertRGB(before,self.s.pixel((.18,.12,.08)))

if __name__=="__main__": unittest.main(verbosity=2)
