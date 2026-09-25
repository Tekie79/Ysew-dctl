"""Alpha.5 category-prefix UI labels."""
from pathlib import Path
import sys, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from ui_schema import parse_ui

class CategoryLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui={c.name:c for c in parse_ui((ROOT/'src/YSEW_Film_Lab.dctl').read_text())}
    def test_input_output_bookends(self):
        controls=parse_ui((ROOT/'src/YSEW_Film_Lab.dctl').read_text())
        self.assertEqual(controls[0].label,'INPUT')
        self.assertEqual(controls[-1].label,'OUTPUT')
    def test_major_slider_prefixes(self):
        expected={
          'exposure':'BAL ','neg_contrast':'NEG ','look_mix':'LOOK ','print_contrast':'PRT ',
          'halation_amount':'HAL ','bloom_amount':'BLM ','glow_amount':'GLW ','grain_amount':'GRN ',
          'vignette_radius':'VIG ','ev_low':'DIAG ','range_hue':'RNG ','cal_target':'CAL ',
          'qc_margin':'QC ','output_gray':'OUT '
        }
        for name,prefix in expected.items():
            self.assertTrue(self.ui[name].label.startswith(prefix),(name,self.ui[name].label))
if __name__=='__main__': unittest.main(verbosity=2)
