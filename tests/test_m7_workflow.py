"""M7 candidate show profiles, shot matching and deterministic release workflow tests."""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys, zipfile, io
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import show_profiles, shot_match, release

class M7WorkflowTests(unittest.TestCase):
    def test_candidate_profiles_validate_and_are_pending(self):
        doc=show_profiles.validate(show_profiles.load())
        self.assertEqual(set(doc['profiles']),{'fall_interior','winter_interior','night','exterior_day','exterior_dusk'})
        for p in doc['profiles'].values():
            self.assertEqual(p['approval_status'],'pending_director_review')
            self.assertNotIn('input_mode',p['settings']); self.assertNotIn('output_mode',p['settings'])
            self.assertNotIn('diag_mode',p['settings'])

    def test_profile_look_indices_match_m7_modes(self):
        doc=show_profiles.validate(show_profiles.load())
        expected={'fall_interior':1,'winter_interior':2,'night':3,'exterior_day':4,'exterior_dusk':5}
        self.assertEqual({k:v['settings']['look_mode'] for k,v in doc['profiles'].items()},expected)

    def _metrics(self,shot,offset=0):
        base={
          'exposure_median_ev':0.0,'shadow_p10_ev':-3.0,'highlight_p90_ev':2.5,
          'neutral_xy_error':0.005,'saturation_median':0.38,'skin_ev_median':0.2,
          'gamut_occupancy_p95':0.72,'black_level_p02':0.018,'highlight_level_p98':0.86}
        base['exposure_median_ev']+=offset
        return {'version':1,'shot_id':shot,'episode':'E01','scene':'S01','frame':100,'stage':'FINAL_REC709',
                'working_space':'DWG_LINEAR','film_lab_version':'0.7.0-alpha.4','show_profile':'fall_interior','metrics':base}

    def test_shot_match_pass_warn_fail(self):
        profile=shot_match.validate_tolerances(shot_match.load_json(ROOT/'presets/yekermo_sew_consistency_v1.json'))
        ref=self._metrics('REF')
        self.assertEqual(shot_match.compare(ref,self._metrics('PASS',.10),profile)['status'],'PASS')
        self.assertEqual(shot_match.compare(ref,self._metrics('WARN',.35),profile)['status'],'WARN')
        self.assertEqual(shot_match.compare(ref,self._metrics('FAIL',.60),profile)['status'],'FAIL')

    def test_stage_mismatch_is_rejected(self):
        profile=shot_match.validate_tolerances(shot_match.load_json(ROOT/'presets/yekermo_sew_consistency_v1.json'))
        ref=self._metrics('REF'); cand=self._metrics('C'); cand['stage']='PRINT'
        with self.assertRaises(ValueError): shot_match.compare(ref,cand,profile)

    def test_batch_uses_manifest_relative_paths(self):
        profile=shot_match.validate_tolerances(shot_match.load_json(ROOT/'presets/yekermo_sew_consistency_v1.json'))
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            (p/'ref.json').write_text(json.dumps(self._metrics('REF')))
            (p/'a.json').write_text(json.dumps(self._metrics('A',.05)))
            (p/'b.json').write_text(json.dumps(self._metrics('B',.30)))
            (p/'manifest.json').write_text(json.dumps({'version':1,'reference':'ref.json','shots':['a.json','b.json']}))
            out=shot_match.batch(p/'manifest.json',profile)
            self.assertEqual(out['status'],'WARN'); self.assertEqual(len(out['results']),2)

    def test_release_package_is_deterministic_and_manifested(self):
        a=release.package_bytes(); b=release.package_bytes()
        self.assertEqual(a,b)
        with zipfile.ZipFile(io.BytesIO(a)) as z:
            names=z.namelist()
            prefix=f'YSEW_Film_Lab_{release.VERSION}/'
            self.assertIn(prefix+'manifest.json',names)
            manifest=json.loads(z.read(prefix+'manifest.json'))
            self.assertFalse(manifest['production_ready'])
            self.assertEqual(manifest['host_acceptance'],'pending_comprehensive_resolve_test')
            self.assertIn('dist/YSEW_Film_Lab_M7_A4.dctl',manifest['files'])

if __name__=='__main__': unittest.main(verbosity=2)
