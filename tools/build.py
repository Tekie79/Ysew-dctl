#!/usr/bin/env python3
"""Reproducible, dependency-free DCTL packaging. Run from any working directory."""
from __future__ import annotations
import argparse
import hashlib
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/YSEW_Film_Lab.dctl'
TARGET = ROOT / 'dist/YSEW_Film_Lab.dctl'
UI_RE = re.compile(r'^DEFINE_UI_PARAMS\((\w+),\s*"([^"]+)",\s*(DCTLUI_\w+),\s*([^,\)]+)', re.M)

def controls(text: str) -> list[tuple[str, str, str, str]]:
    return [tuple(item.strip() for item in match) for match in UI_RE.findall(text)]

def validate(text: str) -> None:
    ui = controls(text)
    if not ui or len(ui) != text.count('\nDEFINE_UI_PARAMS('):
        raise ValueError('Every UI declaration must be one line with a quoted label.')
    names = [item[0] for item in ui]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate UI variable.')
    if any(n > 64 for n in Counter(item[2] for item in ui).values()):
        raise ValueError('Conservative limit: no more than 64 controls of a single type.')
    if text.count('__DEVICE__ float3 transform(') != 1:
        raise ValueError('Expected exactly one Transform DCTL entry point.')
    helper_text = text.split('// Pure helpers:', 1)[1].split('__DEVICE__ float3 transform(', 1)[0]
    for name in names:
        # Strip comments before checking for accidental references to host UI variables.
        code = re.sub(r'//[^\n]*', '', helper_text)
        if re.search(r'\b' + re.escape(name) + r'\b', code):
            raise ValueError(f'Helper references UI variable {name}; pass values explicitly.')

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail rather than repair stale dist files.')
    args = parser.parse_args()
    data = SOURCE.read_bytes()
    validate(data.decode('utf-8'))
    if args.check:
        if not TARGET.exists() or TARGET.read_bytes() != data:
            raise SystemExit('dist is stale. Run python3 tools/build.py')
    else:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(data)
    print(f'{TARGET.relative_to(ROOT)} sha256={hashlib.sha256(data).hexdigest()}')

if __name__ == '__main__':
    main()
