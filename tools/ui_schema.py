"""Strict project-side validation of the documented DCTL UI macro spelling.

This is a source linter, NOT a Resolve UI parser or GPU compiler. Labels and enum
labels are raw tokens; only tooltip bodies are string literals. C++ compilation
alone does not validate this interface (the alpha.1 adapter discarded metadata).
"""
from __future__ import annotations
from collections import Counter
from dataclasses import asdict, dataclass
import json
import math
import re

KINDS = {'DCTLUI_SLIDER_FLOAT', 'DCTLUI_SLIDER_INT', 'DCTLUI_VALUE_BOX', 'DCTLUI_CHECK_BOX',
         'DCTLUI_COMBO_BOX', 'DCTLUI_COLOR_PICKER'}
IDENTIFIER = re.compile(r'[A-Za-z_]\w*\Z', re.ASCII)
NUMBER = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z')
LABEL = re.compile(r'[A-Za-z0-9][A-Za-z0-9 .+\-]*\Z', re.ASCII)

@dataclass(frozen=True)
class Control:
    name: str
    label: str
    kind: str
    values: tuple[str, ...]
    enums: tuple[str, ...] = ()
    choices: tuple[str, ...] = ()

    @property
    def default(self) -> str:
        if self.kind == 'DCTLUI_COLOR_PICKER':
            return 'UIPicker{' + ','.join(self.values) + '}'
        return self.values[0]

    def contract(self) -> dict:
        # JSON roundtrip normalizes tuple fields to lists.
        return json.loads(json.dumps(asdict(self)))


def split_args(body: str) -> list[str]:
    """Split commas except inside braces or a quoted tooltip body."""
    fields, start, depth, quoted, escaped = [], 0, 0, False, False
    for i, ch in enumerate(body):
        if quoted:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth < 0:
                raise ValueError('Unmatched UI brace')
        elif ch == ',' and depth == 0:
            fields.append(body[start:i].strip())
            start = i+1
    if depth or quoted:
        raise ValueError('Unclosed UI list or string')
    fields.append(body[start:].strip())
    if any(not field for field in fields):
        raise ValueError('Empty UI argument')
    return fields


def _label(value: str, limit: int) -> str:
    if not LABEL.fullmatch(value) or len(value) > limit:
        raise ValueError(f'UI label must be an unquoted ASCII label <= {limit} characters: {value!r}')
    return value


def _number(value: str) -> float:
    if not NUMBER.fullmatch(value):
        raise ValueError(f'UI numbers must be plain numeric literals without C suffixes: {value!r}')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Nonfinite UI value')
    return result


def _list(value: str) -> tuple[str, ...]:
    if not value.startswith('{') or not value.endswith('}'):
        raise ValueError('UI enum arrays must use braces')
    return tuple(split_args(value[1:-1]))


def parse_ui(text: str) -> list[Control]:
    if text.startswith('\ufeff') or not text.isascii():
        raise ValueError('DCTL source must be ASCII without a byte-order mark')
    result, tips = [], []
    for line_no, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if line.startswith('//'):
            continue
        macro = next((m for m in ('DEFINE_UI_PARAMS', 'DEFINE_UI_TOOLTIP') if line.startswith(m)), None)
        if macro is None:
            continue
        if not line.startswith(macro+'(') or not line.endswith(')'):
            raise ValueError(f'Line {line_no}: UI macros must occupy a single complete line')
        args = split_args(line[len(macro)+1:-1])
        if macro == 'DEFINE_UI_TOOLTIP':
            if len(args) != 2:
                raise ValueError('Tooltip requires a label and a string')
            label = _label(args[0], 20)
            try:
                body = json.loads(args[1])
            except json.JSONDecodeError as exc:
                raise ValueError('Tooltip text must be a quoted string') from exc
            if not isinstance(body, str) or not body:
                raise ValueError('Empty tooltip body')
            tips.append(label)
            continue
        if len(args) < 4:
            raise ValueError(f'Line {line_no}: incomplete control')
        name, label, kind = args[:3]
        if not IDENTIFIER.fullmatch(name) or kind not in KINDS:
            raise ValueError(f'Line {line_no}: unsupported control name/type')
        _label(label, 20)
        tail = args[3:]
        enums: tuple[str, ...] = ()
        choices: tuple[str, ...] = ()
        if kind == 'DCTLUI_COMBO_BOX':
            if len(tail) != 3:
                raise ValueError('Combo requires default, enum list and label list')
            index = _number(tail[0])
            enums, choices = _list(tail[1]), _list(tail[2])
            if len(enums) != len(choices) or len(set(enums)) != len(enums):
                raise ValueError('Combo values and labels must be unique and one-to-one')
            if not all(IDENTIFIER.fullmatch(item) for item in enums):
                raise ValueError('Combo enum values must be unquoted identifiers')
            for item in choices:
                _label(item, 22)
            if len(set(choices)) != len(choices) or index != int(index) or not 0 <= index < len(enums):
                raise ValueError('Invalid combo labels or default index')
            values = (tail[0],)
        else:
            expected = 4 if kind in ('DCTLUI_SLIDER_FLOAT', 'DCTLUI_SLIDER_INT') else (3 if kind == 'DCTLUI_COLOR_PICKER' else 1)
            if len(tail) != expected:
                raise ValueError(f'Wrong number of {kind} arguments')
            numbers = [_number(v) for v in tail]
            if kind == 'DCTLUI_CHECK_BOX' and numbers[0] not in (0, 1):
                raise ValueError('Checkbox default must be 0 or 1')
            if kind == 'DCTLUI_COLOR_PICKER' and not all(0 <= v <= 1 for v in numbers):
                raise ValueError('Picker defaults must be normalized RGB')
            if expected == 4:
                default, low, high, step = numbers
                if not low <= default <= high or low == high or step <= 0:
                    raise ValueError('Invalid slider range/default/step')
                if kind == 'DCTLUI_SLIDER_INT' and any(v != int(v) for v in numbers):
                    raise ValueError('Integer slider requires integer values')
            values = tuple(tail)
        result.append(Control(name, label, kind, values, enums, choices))
    if not result:
        raise ValueError('No UI controls found')
    names = [c.name for c in result]
    labels = [c.label for c in result]
    enums = [e for c in result for e in c.enums]
    if len(set(names)) != len(names) or len(set(labels)) != len(labels):
        raise ValueError('Duplicate UI name or label')
    if len(set(enums)) != len(enums) or set(enums) & set(names):
        raise ValueError('Duplicate enum identifier or conflict with UI variable')
    if any(n > 64 for n in Counter(c.kind for c in result).values()):
        raise ValueError('More than 64 controls of one type')
    if len(set(tips)) != len(tips) or not set(tips) <= set(labels):
        raise ValueError('Duplicate tooltip or tooltip does not match a control label')
    return result


def controls(text: str) -> list[tuple[str, str, str, str]]:
    return [(c.name, c.label, c.kind, c.default) for c in parse_ui(text)]
