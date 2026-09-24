#!/usr/bin/env python3
"""Validate and inspect versioned Yekermo Sew candidate show profiles."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from ui_schema import parse_ui

SOURCE=ROOT/'src/YSEW_Film_Lab.dctl'
DEFAULT_PROFILES=ROOT/'presets/yekermo_sew_show_profiles_v1.json'

ALLOWED={
    'film_model','negative_on','adv_neg_density','adv_neg_color','adv_neg_sep','adv_neg_shadow','adv_neg_high',
    'adv_neg_warm','adv_neg_green','adv_neg_cool','look_mode','look_mix','skin_protect','print_on',
    'adv_print_black','adv_print_white','adv_print_sep','adv_print_warm','adv_print_color',
    'optics_on','optics_quality','optics_mix','optics_soft','halation_amount','halation_radius',
    'halation_threshold','halation_tint','bloom_amount','bloom_radius','bloom_threshold','glow_amount',
    'glow_radius','glow_threshold','veil_amount','veil_radius','veil_threshold','texture_on','grain_gauge',
    'grain_amount','grain_size','grain_rough','grain_color','grain_shadow','grain_mid','grain_high',
    'grain_motion','grain_seed','lens_soft','lens_radius','micro_soft'
}
REQUIRED_PROFILE_KEYS={'label','approval_status','intent','settings'}

def load(path:Path=DEFAULT_PROFILES):
    return json.loads(path.read_text())

def _num(s):
    return float(s)

def validate(doc, source:Path=SOURCE):
    if doc.get('version') != 1: raise ValueError('show profile version must be 1')
    if doc.get('status') != 'pending_director_review': raise ValueError('top-level status must remain pending_director_review until explicit approval')
    profiles=doc.get('profiles')
    if not isinstance(profiles,dict) or not profiles: raise ValueError('profiles must be a non-empty object')
    controls={c.name:c for c in parse_ui(source.read_text())}
    for pid,p in profiles.items():
        missing=REQUIRED_PROFILE_KEYS-set(p)
        if missing: raise ValueError(f'{pid}: missing {sorted(missing)}')
        if p['approval_status'] != 'pending_director_review':
            raise ValueError(f'{pid}: cannot claim director approval before recorded review')
        settings=p['settings']
        if not isinstance(settings,dict) or not settings: raise ValueError(f'{pid}: empty settings')
        if 'look_mode' not in settings: raise ValueError(f'{pid}: look_mode required')
        for name,value in settings.items():
            if name not in ALLOWED: raise ValueError(f'{pid}: technical/unknown setting not allowed: {name}')
            if name not in controls: raise ValueError(f'{pid}: setting absent from DCTL: {name}')
            c=controls[name]
            if c.kind in ('DCTLUI_COMBO_BOX','DCTLUI_CHECK_BOX','DCTLUI_SLIDER_INT'):
                if isinstance(value,bool) or int(value) != value: raise ValueError(f'{pid}.{name}: integer value required')
                iv=int(value)
                if c.kind=='DCTLUI_COMBO_BOX' and not (0 <= iv < len(c.enums)):
                    raise ValueError(f'{pid}.{name}: combo index out of range')
                if c.kind=='DCTLUI_CHECK_BOX' and iv not in (0,1):
                    raise ValueError(f'{pid}.{name}: checkbox must be 0/1')
                if c.kind=='DCTLUI_SLIDER_INT':
                    lo,hi=_num(c.values[1]),_num(c.values[2])
                    if not lo <= iv <= hi: raise ValueError(f'{pid}.{name}: outside [{lo},{hi}]')
            elif c.kind=='DCTLUI_SLIDER_FLOAT':
                fv=float(value); lo,hi=_num(c.values[1]),_num(c.values[2])
                if not lo <= fv <= hi: raise ValueError(f'{pid}.{name}: outside [{lo},{hi}]')
            else:
                raise ValueError(f'{pid}.{name}: unsupported profile control type {c.kind}')
    return doc

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profiles',type=Path,default=DEFAULT_PROFILES)
    sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('validate')
    sub.add_parser('list')
    show=sub.add_parser('show'); show.add_argument('profile')
    args=ap.parse_args()
    doc=validate(load(args.profiles))
    if args.cmd=='validate':
        print(f"OK: {len(doc['profiles'])} candidate profiles")
    elif args.cmd=='list':
        for pid,p in doc['profiles'].items(): print(f"{pid}\t{p['label']}\t{p['approval_status']}")
    else:
        if args.profile not in doc['profiles']: raise SystemExit(f'unknown profile: {args.profile}')
        print(json.dumps(doc['profiles'][args.profile],indent=2,sort_keys=True))

if __name__=='__main__':
    main()
