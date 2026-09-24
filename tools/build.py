#!/usr/bin/env python3
"""Dependency-free, deterministic DCTL packaging and strict UI source lint."""
from __future__ import annotations
import argparse
import hashlib
import re
from pathlib import Path
from ui_schema import controls, parse_ui  # controls is also used by the native test adapter.

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src/YSEW_Film_Lab.dctl'
TARGET = ROOT / 'dist/YSEW_Film_Lab.dctl'
VERSION = '0.7.0-alpha.1'


def validate(text: str) -> None:
    ui = parse_ui(text)
    shader = text.split('// Pure helpers:', 1)[-1]
    shader = re.sub(r'//[^\n]*', '', shader)
    # GPU languages reserve type/address-space names absent from ordinary C++.
    # This targeted guard is not a substitute for a Metal/OpenCL compilation.
    if re.search(r'\b(?:float|int|float3)\s+(?:half|kernel|constant|thread|device|sampler)\b', shader):
        raise ValueError('GPU-reserved type/address-space name used as a local identifier')
    if text.count('__DEVICE__ float3 transform(') != 1:
        raise ValueError('Expected exactly one Transform DCTL entry point')
    if '// Pure helpers:' in text:
        helper_text = text.split('// Pure helpers:', 1)[1].split('__DEVICE__ float3 transform(', 1)[0]
        code = re.sub(r'//[^\n]*', '', helper_text)
        for c in ui:
            if re.search(r'\b'+re.escape(c.name)+r'\b', code):
                raise ValueError(f'Helper references global UI variable {c.name}; pass values explicitly')


def outputs() -> dict[Path, bytes]:
    files = {}
    for source in sorted((ROOT/'src').glob('*.dctl')):
        data = source.read_bytes()
        validate(data.decode('ascii'))
        files[ROOT/'dist'/source.name] = data
    # Keep prior version-distinct files immutable; the current milestone gets its own alias.
    files[ROOT/'dist/YSEW_Film_Lab_M7.dctl'] = SOURCE.read_bytes()
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail rather than repair stale dist files')
    args = parser.parse_args()
    for path, data in outputs().items():
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                raise SystemExit(f'{path.name} is stale; run python3 tools/build.py')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        print(f'{path.relative_to(ROOT)} sha256={hashlib.sha256(data).hexdigest()}')


if __name__ == '__main__':
    main()
