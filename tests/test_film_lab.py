"""Execute the shipped shader as float32 C++ through a small CPU compatibility shim.
These tests do NOT establish Resolve, Metal, CUDA, OpenCL, UI or playback support.
No third-party Python packages, media, network access or proprietary SDK required.
"""
from __future__ import annotations
import ctypes as C
import hashlib
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build import SOURCE, TARGET, controls, validate

from native import Shader
from ui_schema import parse_ui

class FilmLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Shader()
    @classmethod
    def tearDownClass(cls):
        cls.s.temp.cleanup()
    def setUp(self):
        self.s.reset()
        self.s.set(input_mode=1, diag_legend=0)
    def assertRGB(self, actual, expected, tol=3e-6):
        for a, b in zip(actual, expected):
            self.assertTrue(math.isclose(a,b,rel_tol=tol,abs_tol=tol), (actual,expected))
    def bypass(self, output=1):
        self.s.set(negative_on=0,print_on=0,look_mode=0,vignette_stops=0,output_mode=output)

    def test_01_published_intermediate_vectors(self):
        for linear, code in [(-.01,-.104443),(0,0),(.18,.336043),(1,.513837),(10,.756599),(40,.903125),(100,1)]:
            self.assertAlmostEqual(self.s.scalar(1,linear),code,delta=6e-7)
    def test_02_intermediate_roundtrip_extended_range(self):
        for v in [-.1,-.01,0,1e-8,.001,.00262409,.18,1,4,40,100,1000]:
            self.assertTrue(math.isclose(self.s.scalar(0,self.s.scalar(1,v)),v,rel_tol=4e-6,abs_tol=1e-7))
    def test_03_intermediate_cut_continuity(self):
        self.assertLess(abs(self.s.scalar(1,.002624089)-self.s.scalar(1,.002624091)),1e-7)
    def test_04_dwg_published_matrix(self):
        self.assertRGB(self.s.vector(0,(1,0,0)),(.70062239,.27411851,-.09896291))
        self.assertRGB(self.s.vector(0,(0,1,0)),(.14877482,.87363190,-.13789533))
        self.assertRGB(self.s.vector(0,(0,0,1)),(.10105872,-.14775041,1.32591599))
    def test_05_d65_neutral_and_709_primary(self):
        self.assertRGB(self.s.vector(2,(1,1,1)),(1,1,1))
        # Independently specified BT.709 red primary in XYZ after a working-space roundtrip.
        self.assertRGB(self.s.vector(0,self.s.vector(3,(1,0,0))),(.412390799,.212639006,.019330819))
    def test_06_matrix_roundtrips(self):
        rng=random.Random(6)
        for _ in range(300):
            v=tuple(rng.uniform(-.3,20) for _ in range(3))
            self.assertRGB(self.s.vector(3,self.s.vector(2,v)),v,tol=2e-5)
    def test_07_stop_reference(self):
        for ev in range(-16,17):
            self.assertAlmostEqual(self.s.scalar(2,.18*2**ev,.18),ev,delta=2e-6)
        self.assertLess(self.s.scalar(2,0,.18),-90)
        self.assertLess(self.s.scalar(2,-.1,.18),-90)
    def test_08_exposure_stops_and_zero_balance(self):
        self.bypass(); sample=(.18,.07,-.01)
        self.assertRGB(self.s.pixel(sample),sample)
        self.s.set(exposure=1)
        self.assertRGB(self.s.pixel(sample),tuple(v*2 for v in sample))
    def test_09_printer_density_calibration(self):
        self.bypass(); self.s.set(printer_r=1,printer_g=1,printer_b=1)
        self.assertRGB(self.s.pixel((.18,)*3),(.18*10**(-.025),)*3)
    def test_10_negative_curve_gray_anchor(self):
        for contrast in [.5,1,1.08,2]:
            self.assertAlmostEqual(self.s.scalar(6,.18,contrast,.4,.4),.18,delta=1e-6)
    def test_11_negative_curve_monotonic_extremes(self):
        for contrast,toe,shoulder in [(.5,.4,.4),(2,.4,.4),(1.08,.08,.16),(1,0,0)]:
            values=[self.s.scalar(6,.18*2**(i/8),contrast,toe,shoulder) for i in range(-128,129)]
            self.assertTrue(all(a<b for a,b in zip(values,values[1:])))
    def test_12_bypass_retains_negative_working_values(self):
        self.bypass(); self.assertRGB(self.s.pixel((-.01,.1,4)),(-.01,.1,4))
    def test_13_di_working_identity(self):
        self.bypass(output=0); self.s.set(input_mode=0)
        v=(-.01,.336043,.903125); self.assertRGB(self.s.pixel(v),v)
    def test_14_output_gray_calibration(self):
        self.bypass(output=2)
        for gray in [.25,.42,.65]:
            self.s.set(output_gray=gray)
            self.assertRGB(self.s.pixel((.18,)*3),(gray,)*3)
    def test_15_tone_curve_monotonic_and_unbounded_scene(self):
        values=[self.s.scalar(3,2**(i/8),.42) for i in range(-128,129)]
        self.assertTrue(all(0<a<1 for a in values))
        self.assertTrue(all(a<b for a,b in zip(values,values[1:])))
    def test_16_gamut_compression_bounds_and_luminance(self):
        rng=random.Random(16)
        for _ in range(500):
            v=tuple(rng.uniform(-.5,1.5) for _ in range(3))
            y=sum(a*b for a,b in zip(v,(.212639006,.715168679,.072192315)))
            if .001 < y < .999:
                out=self.s.vector(5,v,.8)
                self.assertTrue(all(-2e-6 <= a <= 1.000002 for a in out))
                self.assertAlmostEqual(sum(a*b for a,b in zip(out,(.212639006,.715168679,.072192315))),y,delta=2e-6)
    def test_17_gamut_neutral_identity(self):
        for y in [0,.001,.18,.5,.999,1]:
            self.assertRGB(self.s.vector(5,(y,)*3,.8),(y,)*3)
    def test_18_source_exposure_independent_of_grade(self):
        self.s.set(diag_mode=2,diag_tap=0,ev_step=0)
        a=self.s.pixel((.18,)*3)
        self.s.set(exposure=4,look_mode=2,print_density=.2,output_gray=.6)
        self.assertRGB(self.s.pixel((.18,)*3),a)
        self.assertRGB(a,(.5,)*3)
    def test_19_balanced_exposure_tap(self):
        self.s.set(diag_mode=2,diag_tap=1,ev_step=0,exposure=2)
        self.assertRGB(self.s.pixel((.18,)*3),(.5+2/12,)*3)
    def test_20_nonpositive_exposure_not_middle_gray(self):
        self.s.set(diag_mode=1)
        self.assertRGB(self.s.pixel((0,0,0)),(0,0,0))
        self.s.set(diag_mode=2)
        self.assertRGB(self.s.pixel((-.1,-.1,-.1)),(0,0,0))
    def test_21_hue_wrap_and_full_circle(self):
        self.assertEqual(self.s.scalar(4,359,1,3,0),1)
        self.assertEqual(self.s.scalar(4,1,359,3,0),1)
        self.assertEqual(self.s.scalar(4,180,0,3,0),0)
        self.assertEqual(self.s.scalar(4,180,0,180,0),1)
    def test_22_ranges_sort_inverted_bounds(self):
        for x in [-4,-2.1,-2,0,2,2.1,4]:
            self.assertEqual(self.s.scalar(5,x,-2,2,.2),self.s.scalar(5,x,2,-2,.2))
    def test_23_color_range_neutrals_have_no_hue(self):
        self.s.set(diag_mode=13,range_smin=0,range_smax=1,range_width=20)
        self.assertRGB(self.s.pixel((.18,)*3),(0,0,0))
        self.s.set(range_width=180)
        self.assertRGB(self.s.pixel((.18,)*3),(1,1,1))
    def test_24_skin_candidate_independent_of_look(self):
        rgb=self.s.vector(3,(.18,.09,.06)); self.s.set(diag_mode=15)
        original=self.s.pixel(rgb)
        self.s.set(look_mode=2,output_gray=.65,print_density=.3)
        self.assertRGB(self.s.pixel(rgb),original)
        self.assertGreater(original[0],.5)
    def test_25_skin_candidate_has_no_brightness_gate(self):
        self.s.set(diag_mode=15)
        for scale in [.005,.01,.1,1,2]:
            rgb=self.s.vector(3,(.18*scale,.09*scale,.06*scale))
            self.assertGreater(self.s.pixel(rgb)[0],.2)
    def test_26_no_di_diagnostic_passthrough(self):
        self.s.set(diag_mode=2,output_mode=0)
        warning=self.s.pixel((.18,)*3)
        self.assertNotEqual(warning,(.5,.5,.5))
    def test_27_no_effect_difference_is_black(self):
        self.bypass(output=2); self.s.set(diag_mode=24)
        self.assertRGB(self.s.pixel((.18,.15,.09)),(0,0,0))
    def test_28_inspect_final_matches_output(self):
        v=(.18,.13,.09); normal=self.s.pixel(v)
        self.s.set(diag_mode=25,inspect_stage=7)
        self.assertRGB(self.s.pixel(v),normal)
    def test_29_vignette_center_and_edges(self):
        self.bypass(); self.s.set(vignette_stops=2)
        center=self.s.pixel((.18,)*3,w=101,h=101,x=50,y=50)
        edge=self.s.pixel((.18,)*3,w=101,h=101,x=0,y=0)
        self.assertRGB(center,(.18,)*3)
        self.assertLess(edge[0],center[0]*.3)
    def test_30_di_input_matches_linear_exposure(self):
        self.s.set(diag_mode=2,ev_step=0)
        for ev in [-8,-2,0,2,8]:
            linear=.18*2**ev
            self.s.set(input_mode=1); a=self.s.pixel((linear,)*3)
            self.s.set(input_mode=0); b=self.s.pixel((self.s.scalar(1,linear),)*3)
            self.assertRGB(a,b)
    def test_31_invalid_input_is_visible(self):
        for value in [float('nan'),float('inf'),-float('inf'),1e30]:
            out=self.s.pixel((value,.18,.18),x=16,y=16)
            self.assertRGB(out,(1,0,.65))
    def test_32_scene_low_channel_map(self):
        self.s.set(diag_mode=18)
        self.assertRGB(self.s.pixel((-.01,.1,0)),(1,0,1))
    def test_33_bright_neutral_not_chromaticity_error(self):
        self.bypass(output=2); self.s.set(diag_mode=20)
        self.assertRGB(self.s.pixel((20,)*3),(.1,.65,.2))
    def test_34_out_of_709_chromaticity(self):
        self.bypass(output=2); self.s.set(diag_mode=20)
        # DWG saturated red lies outside the 709 triangle.
        self.assertRGB(self.s.pixel((1,0,0)),(1,.05,.1))
    def test_35_zone_five_is_middle_gray(self):
        self.s.set(diag_mode=3)
        self.assertRGB(self.s.pixel((.18,)*3),(.5,)*3)
    def test_36_warning_strip_cannot_be_disabled(self):
        self.s.set(diag_mode=7,diag_legend=0)
        self.assertRGB(self.s.pixel((.18,)*3,x=0,y=0),(1,.6,0))
    def test_37_quantization(self):
        self.assertEqual(self.s.scalar(7,.3,0),C.c_float(.3).value)
        self.assertEqual(self.s.scalar(7,.3,1),0)
        self.assertEqual(self.s.scalar(7,.3,2),.5)
        self.assertAlmostEqual(self.s.scalar(7,.3,3),1/3,delta=1e-7)
    def test_38_all_diagnostic_modes_finite_and_bounded(self):
        rng=random.Random(38)
        for mode in range(27):
            self.s.set(diag_mode=mode)
            for _ in range(80):
                rgb=tuple(rng.uniform(-.2,64) for _ in range(3))
                out=self.s.pixel(rgb)
                self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in out),(mode,rgb,out))
    def test_39_randomized_controls_finite(self):
        rng=random.Random(39)
        for _ in range(700):
            self.s.set(exposure=rng.uniform(-10,10),warm=rng.uniform(-1,1),tint=rng.uniform(-1,1),
                neg_contrast=rng.uniform(.5,2),neg_toe=rng.uniform(0,.4),neg_shoulder=rng.uniform(0,.4),
                print_contrast=rng.uniform(.5,2),print_toe=rng.uniform(0,.4),print_shoulder=rng.uniform(0,.4),
                print_density=rng.uniform(-.3,.3),look_mode=rng.randrange(3),gamut_knee=rng.uniform(.1,.95))
            out=self.s.pixel(tuple(rng.uniform(-1,64) for _ in range(3)))
            self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in out),out)
    def test_40_ui_contract(self):
        text=SOURCE.read_text(); validate(text)
        actual=[c.contract() for c in parse_ui(text)]
        saved=json.loads((ROOT/'tests/ui_contract.json').read_text())
        self.assertEqual(actual,saved)
    def test_41_reproducible_distribution(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),hashlib.sha256(TARGET.read_bytes()).hexdigest())
    def test_42_hue_map_primary_colors(self):
        for h,rgb in [(0,(1,0,0)),(60,(1,1,0)),(120,(0,1,0)),(180,(0,1,1)),(240,(0,0,1)),(300,(1,0,1)),(360,(1,0,0))]:
            self.assertRGB(self.s.vector(7,(0,0,0),h),rgb)
    def test_43_digit_patterns(self):
        patterns=['111101101101111','010110010010111','111001111100111','111001111001111',
                  '101101111001001','111100111001111','111100111101111','111001001001001',
                  '111101111101111','111101111001111']
        for digit,pattern in enumerate(patterns):
            actual=''.join(str(int(self.s.scalar(8,digit,x,y))) for y in range(5) for x in range(3))
            self.assertEqual(actual,pattern)

if __name__ == '__main__':
    unittest.main(verbosity=2)
