#!/usr/bin/env python3
"""Build a deterministic Yekermo Sew Film Lab release ZIP and validate release safety defaults."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build import SOURCE, VERSION, outputs
from ui_schema import parse_ui
from show_profiles import load as load_profiles, validate as validate_profiles
from shot_match import load_json, validate_tolerances

PACKAGE_NAME=f"YSEW_Film_Lab_{VERSION}"
REQUIRED=[
    Path('dist/YSEW_Film_Lab_M7.dctl'),
    Path('README.md'),
    Path('docs/RESOLVE_SETUP.md'),
    Path('docs/DIAGNOSTICS.md'),
    Path('docs/M7_SHOW_MASTERING.md'),
    Path('docs/DELIVERY_QC.md'),
    Path('presets/yekermo_sew_show_profiles_v1.json'),
    Path('presets/yekermo_sew_consistency_v1.json'),
    Path('schemas/ysew-shot-metrics-v1.schema.json'),
    Path('tools/shot_match.py'),
]
DEBUG_DEFAULTS={'diag_mode':'0','guide_mode':'0','optics_view':'0','texture_view':'0'}

def sha(data:bytes): return hashlib.sha256(data).hexdigest()

def validate_inputs():
    for path,data in outputs().items():
        if not path.exists() or path.read_bytes()!=data: raise ValueError(f'stale distribution: {path}')
    if (ROOT/'dist/YSEW_Film_Lab_M7.dctl').read_bytes()!=SOURCE.read_bytes():
        raise ValueError('M7 alias must be byte-identical to canonical source')
    controls={c.name:c for c in parse_ui(SOURCE.read_text())}
    for name,expected in DEBUG_DEFAULTS.items():
        if controls[name].values[0] != expected: raise ValueError(f'{name} must default Off')
    if controls['output_mode'].values[0] != '2': raise ValueError('internal Rec709 remains the default M7 output owner')
    validate_profiles(load_profiles())
    validate_tolerances(load_json(ROOT/'presets/yekermo_sew_consistency_v1.json'))
    missing=[str(p) for p in REQUIRED if not (ROOT/p).is_file()]
    if missing: raise ValueError(f'missing package files: {missing}')

def package_bytes():
    validate_inputs()
    payload={}
    for rel in REQUIRED:
        data=(ROOT/rel).read_bytes()
        payload[str(rel).replace('\\','/')]=data
    manifest={
        'format_version':1,'product':'Yekermo Sew Film Lab','version':VERSION,
        'production_ready':False,
        'host_acceptance':'pending_comprehensive_resolve_test',
        'files':{name:{'sha256':sha(data),'bytes':len(data)} for name,data in sorted(payload.items())}
    }
    payload['manifest.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(payload.items()):
            info=zipfile.ZipInfo(f'{PACKAGE_NAME}/{name}',date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            info.create_system=3
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return buf.getvalue()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true')
    ap.add_argument('--output',type=Path,default=ROOT/'artifacts'/f'{PACKAGE_NAME}.zip')
    args=ap.parse_args()
    a=package_bytes()
    if args.check:
        b=package_bytes()
        if a!=b: raise SystemExit('release package is not deterministic')
        print(f'OK {PACKAGE_NAME}.zip sha256={sha(a)} bytes={len(a)}')
        return
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_bytes(a)
    print(f'{args.output} sha256={sha(a)} bytes={len(a)}')

if __name__=='__main__':
    main()
