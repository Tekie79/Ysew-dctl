#!/usr/bin/env python3
"""Compare Yekermo Sew shot metrics against a reference and batch episode manifests."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_PROFILE=ROOT/'presets/yekermo_sew_consistency_v1.json'
VALID_STAGES={'BALANCED','LOOK','PRINT','FINAL_REC709'}
VALID_SPACES={'DWG_LINEAR','DWG_INTERMEDIATE'}
RANK={'PASS':0,'WARN':1,'FAIL':2}

def load_json(path:Path):
    return json.loads(path.read_text())

def validate_tolerances(doc):
    if doc.get('version') != 1: raise ValueError('tolerance version must be 1')
    metrics=doc.get('metrics')
    if not isinstance(metrics,dict) or not metrics: raise ValueError('tolerance metrics required')
    warn=float(doc.get('warn_multiplier',1.0)); fail=float(doc.get('fail_multiplier',2.0))
    if warn <= 0 or fail <= warn: raise ValueError('require 0 < warn_multiplier < fail_multiplier')
    for k,v in metrics.items():
        if not isinstance(v,dict) or float(v.get('tolerance',0)) <= 0: raise ValueError(f'invalid tolerance: {k}')
    return doc

def validate_metrics(doc, required=None):
    if doc.get('version') != 1: raise ValueError('shot metrics version must be 1')
    if not doc.get('shot_id'): raise ValueError('shot_id required')
    if doc.get('stage') not in VALID_STAGES: raise ValueError('invalid stage')
    if doc.get('working_space') not in VALID_SPACES: raise ValueError('invalid working_space')
    metrics=doc.get('metrics')
    if not isinstance(metrics,dict): raise ValueError('metrics object required')
    for k,v in metrics.items():
        if isinstance(v,bool) or not isinstance(v,(int,float)): raise ValueError(f'metric {k} must be numeric')
    if required:
        missing=set(required)-set(metrics)
        if missing: raise ValueError(f"missing metrics: {sorted(missing)}")
    return doc

def compare(reference,candidate,profile):
    p=validate_tolerances(profile)
    required=p['metrics'].keys()
    r=validate_metrics(reference,required); c=validate_metrics(candidate,required)
    if r['stage'] != c['stage']: raise ValueError('reference/candidate stage mismatch')
    if r['working_space'] != c['working_space']: raise ValueError('reference/candidate working-space mismatch')
    warn=float(p['warn_multiplier']); fail=float(p['fail_multiplier'])
    results={}
    overall='PASS'
    for key,spec in p['metrics'].items():
        rv=float(r['metrics'][key]); cv=float(c['metrics'][key]); delta=abs(cv-rv); tol=float(spec['tolerance'])
        ratio=delta/tol
        status='PASS' if ratio <= warn else ('WARN' if ratio <= fail else 'FAIL')
        if RANK[status] > RANK[overall]: overall=status
        results[key]={
            'reference':rv,'candidate':cv,'delta':delta,'tolerance':tol,'ratio':ratio,
            'unit':spec.get('unit',''),'status':status
        }
    return {
        'version':1,'reference_shot':r['shot_id'],'candidate_shot':c['shot_id'],
        'stage':r['stage'],'working_space':r['working_space'],'status':overall,'metrics':results
    }

def text_report(result):
    lines=[f"{result['status']}: {result['candidate_shot']} vs {result['reference_shot']} ({result['stage']})"]
    for k,v in result['metrics'].items():
        lines.append(f"{v['status']:4} {k:24} delta={v['delta']:.6g} tol={v['tolerance']:.6g} ratio={v['ratio']:.2f}")
    return '\n'.join(lines)

def batch(manifest_path:Path,profile):
    manifest=load_json(manifest_path)
    if manifest.get('version') != 1: raise ValueError('batch manifest version must be 1')
    base=manifest_path.parent
    reference=load_json((base/manifest['reference']).resolve())
    results=[]
    overall='PASS'
    for item in manifest.get('shots',[]):
        candidate=load_json((base/item).resolve())
        result=compare(reference,candidate,profile); results.append(result)
        if RANK[result['status']] > RANK[overall]: overall=result['status']
    if not results: raise ValueError('batch shots must not be empty')
    return {'version':1,'status':overall,'reference_shot':reference['shot_id'],'results':results}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profile',type=Path,default=DEFAULT_PROFILE)
    ap.add_argument('--format',choices=['text','json'],default='text')
    sub=ap.add_subparsers(dest='cmd',required=True)
    cp=sub.add_parser('compare'); cp.add_argument('--reference',type=Path,required=True); cp.add_argument('--candidate',type=Path,required=True)
    bp=sub.add_parser('batch'); bp.add_argument('--manifest',type=Path,required=True)
    args=ap.parse_args(); profile=validate_tolerances(load_json(args.profile))
    if args.cmd=='compare':
        result=compare(load_json(args.reference),load_json(args.candidate),profile)
        print(json.dumps(result,indent=2,sort_keys=True) if args.format=='json' else text_report(result))
        raise SystemExit(0 if result['status']=='PASS' else (1 if result['status']=='WARN' else 2))
    result=batch(args.manifest,profile)
    if args.format=='json': print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print(f"{result['status']}: batch vs {result['reference_shot']}")
        for r in result['results']: print(text_report(r))
    raise SystemExit(0 if result['status']=='PASS' else (1 if result['status']=='WARN' else 2))

if __name__=='__main__':
    main()
