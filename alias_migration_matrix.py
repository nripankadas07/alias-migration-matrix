"""Generate bounded wire-key migration witnesses with real Pydantic validation."""
from itertools import product
import json
import pydantic
from pydantic import AliasChoices, ConfigDict, Field, ValidationError, create_model

TYPES = {'int': int, 'str': str, 'bool': bool}


def build(config, label):
    if not isinstance(config, dict):
        raise ValueError('model configuration must be an object')
    fields = config.get('fields')
    if not isinstance(fields, list) or not 1 <= len(fields) <= 6:
        raise ValueError('each model needs 1..6 fields')
    args, keys = {}, {}
    for f in fields:
        if not isinstance(f, dict):
            raise ValueError('fields must contain objects')
        name, kind = f.get('name'), f.get('type')
        aliases = f.get('aliases', [name])
        if not isinstance(name, str) or not name.isidentifier() or name.startswith('_') or name in args or hasattr(pydantic.BaseModel, name) or kind not in TYPES:
            raise ValueError('invalid, duplicate or reserved field name/type')
        if not isinstance(aliases, list) or not 1 <= len(aliases) <= 4 or any(not isinstance(k, str) or not k or len(k) > 80 for k in aliases) or len(set(aliases)) != len(aliases):
            raise ValueError('aliases require 1..4 unique nonempty strings')
        keys[name] = aliases + ([name] if config.get('validate_by_name', False) and name not in aliases else [])
        args[name] = (TYPES[kind], Field(validation_alias=AliasChoices(*aliases)))
    extra = config.get('extra', 'ignore')
    if extra not in ('ignore', 'forbid') or type(config.get('validate_by_name', False)) is not bool:
        raise ValueError('extra must be ignore/forbid; validate_by_name must be boolean')
    return create_model(label, __config__=ConfigDict(extra=extra, validate_by_name=config.get('validate_by_name', False)), **args), keys


def analyze(spec):
    old, oldkeys = build(spec.get('old', {}), 'Before')
    new, newkeys = build(spec.get('new', {}), 'After')
    # Generate candidates from both schemas; tests exercise the actual model, not a
    # hand-written approximation of Pydantic precedence or coercion rules.
    names = list(dict.fromkeys([*oldkeys, *newkeys]))
    options, samples = {}, {}
    for i, name in enumerate(names):
        options[name] = list(dict.fromkeys(oldkeys.get(name, []) + newkeys.get(name, [])))
        field = old.model_fields.get(name) or new.model_fields[name]
        samples[name] = f'{name}:sample' if field.annotation is str else (i + 10 if field.annotation is int else bool(i % 2))
    total = 1
    for values in options.values():
        total *= len(values)
    if total > 512:
        raise ValueError('wire-key combinations exceed 512; reduce fields/aliases')
    candidates = [{}]
    for selected in product(*(options[n] for n in names)):
        candidates.append(dict(zip(selected, (samples[n] for n in names))))
    # Deliberately conflicting aliases expose changes in first-choice precedence.
    baseline = {options[n][0]: samples[n] for n in names}
    for name in names:
        if len(options[name]) > 1:
            payload = baseline.copy()
            for i, key in enumerate(options[name]):
                sample = samples[name]
                payload[key] = sample + f':{i}' if isinstance(sample, str) else (bool(i % 2) if isinstance(sample, bool) else sample + i)
            candidates.append(payload)
    unique = {json.dumps(p, sort_keys=True): p for p in candidates}
    def validate(model, payload):
        try:
            return {'accepted': True, 'values': model.model_validate(payload).model_dump(mode='json')}
        except ValidationError as error:
            return {'accepted': False, 'errors': [{'location': list(e['loc']), 'type': e['type']} for e in error.errors()]}
    rows = []
    for payload in unique.values():
        before, after = validate(old, payload), validate(new, payload)
        change = ('REJECTED_AFTER' if before['accepted'] and not after['accepted'] else
                  'ACCEPTED_AFTER' if not before['accepted'] and after['accepted'] else
                  'VALUE_CHANGED' if before['accepted'] and after['accepted'] and before['values'] != after['values'] else 'UNCHANGED')
        rows.append({'payload': payload, 'old': before, 'new': after, 'change': change})
    return {'pydantic_version': pydantic.__version__, 'tested_payloads': len(rows), 'counts': {c: sum(r['change'] == c for r in rows) for c in ['REJECTED_AFTER', 'ACCEPTED_AFTER', 'VALUE_CHANGED', 'UNCHANGED']}, 'cases': rows,
            'scope': 'Required flat int/str/bool fields and string AliasChoices only. Generated samples are migration witnesses, not exhaustive value compatibility or arbitrary user-model validation.'}


import argparse
import html
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description='Generate payload witnesses for rejected aliases and changed precedence during a model migration.')
    parser.add_argument('input', type=Path, help='JSON scenario, at most 1 MiB')
    parser.add_argument('--html', type=Path, help='write an escaped, offline report')

    args = parser.parse_args()
    try:
        with args.input.open('rb') as handle:
            raw = handle.read(1048577)
        if len(raw) > 1048576:
            raise ValueError('input exceeds 1 MiB')
        spec = json.loads(raw)
        if not isinstance(spec, dict):
            raise ValueError('input must be a JSON object')
        result = analyze(spec)

        output = json.dumps(result, indent=2, allow_nan=False)
        if args.html:
            def show(value):
                if isinstance(value, dict):
                    return '<dl>' + ''.join('<dt>' + html.escape(str(k)) + '</dt><dd>' + show(v) + '</dd>' for k, v in value.items()) + '</dl>'
                if isinstance(value, list):
                    return '<ol>' + ''.join('<li>' + show(v) + '</li>' for v in value) + '</ol>'
                return '<span>' + html.escape(str(value)) + '</span>'
            page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + 'Alias Migration Matrix' + '</title><style>body{max-width:1000px;margin:40px auto;padding:0 20px;font:16px/1.5 system-ui;color:#16324f;background:#f8fafc}h1{font-size:30px}dl{display:grid;grid-template-columns:minmax(150px,1fr) 3fr;gap:5px 20px}dt{font-weight:600;overflow-wrap:anywhere}dd{margin:0;overflow-wrap:anywhere}ol{padding-left:25px}li{padding:10px;border-bottom:1px solid #cbd5e1}span{white-space:pre-wrap}@media(max-width:600px){dl{display:block}dd{margin-bottom:15px}}</style><h1>' + 'Alias Migration Matrix' + '</h1><p>Local diagnostic report. Review the documented scope before acting on a finding.</p>' + show(result) + '</html>'
            args.html.write_text(page, encoding='utf-8')
        print(output)
        return 0
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as error:
        print('error: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
