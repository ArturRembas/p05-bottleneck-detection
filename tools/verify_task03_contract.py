#!/usr/bin/env python3
"""Design-only checks of TASK-03 draft schemas and synthetic fixtures.

Not a parser, normalizer, approval validator, PM4Py integration or product test.
Run from any directory with Python and jsonschema installed.
"""
import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from xml.etree import ElementTree as ET
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / 'examples' / 'event_logs'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def read_csv(name):
    with (EX / name).open(encoding='utf-8', newline='') as source:
        return list(csv.DictReader(source))

def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)

def seconds(end, start):
    return (instant(end) - instant(start)).total_seconds()

def sha(name):
    return hashlib.sha256((EX / name).read_bytes()).hexdigest()

def main():
    print(f'Python {platform.python_version()} | jsonschema {version("jsonschema")}')
    print('Scope: structural validation and independent synthetic fixture oracles only.')
    validators = {}
    for name, file in [('canonical', 'canonical_event_log.schema.json'), ('mapping', 'event_log_mapping.schema.json')]:
        schema = load(ROOT / 'schemas' / file)
        Draft202012Validator.check_schema(schema)
        validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
        print(f'PASS metaschema: {file}')
    cases = load(EX / 'validation_cases.json')['cases']
    require([c['id'] for c in cases] == [f'VC-{n:02}' for n in range(1,21)], 'Case catalogue IDs')
    checks = [dict(file='canonical_log.json', schema='canonical', valid=True), dict(file='confirmed_mapping.example.json', schema='mapping', valid=True)]
    for case in cases:
        for file in case['fixtures']:
            require((EX / file).is_file(), f"Missing fixture: {file}")
        checks.extend(case.get('schema_checks', []))
    for check in checks:
        errors = list(validators[check['schema']].iter_errors(load(EX / check['file'])))
        require((not errors) == check['valid'], f"Unexpected validation result: {check['file']}: {errors}")
        print(f"PASS structural expectation ({'accept' if check['valid'] else 'reject'}): {check['file']}")
    print(f'PASS {len(cases)} catalogue entries and fixture references; {len(checks)} structural expectations.')

    m = load(EX / 'confirmed_mapping.example.json')
    log = load(EX / 'canonical_log.json')
    metadata = log['metadata']
    report = load(EX / 'quality_report.example.json')
    source = read_csv('mapping_source.csv')[0]
    require(sha('mapping_source.csv') == m['input_sha256'], 'Source bytes changed')
    for key in ('schema_version','input_sha256','source_format','mapping_id','mapping_version','case_notion','timestamp_semantics','source_timezone'):
        require(metadata[key] == m[key], f'Mapping/log mismatch: {key}')
    for key in ('mapping_id','mapping_version','input_sha256'):
        require(m['approval'][key] == m[key] == report[key], f'Illustrative reference mismatch: {key}')
    require(metadata['quality_report_ref'] == report['quality_report_ref'], 'Quality report reference')
    event = log['events'][0]
    require(event['case_id'] == source['Order_ID'] == '0007', 'Leading zeros')
    require(event['activity'] == source['Operation'], 'Mapped activity')
    require(instant(event['timestamp']) == instant(source['Recorded_At']), 'Mapped instant')
    require(event['source_event_index'] == 0 and report['input_event_count'] == report['normalized_event_count'] == 1 and report['excluded_event_count'] == 0, 'Illustrative count')
    print('PASS VC-17 source checksum, illustrative mapping references, UTC and identity preservation (not trusted approval).')

    r = read_csv('completion_only.csv')
    gaps = [seconds(y['timestamp'], x['timestamp']) for x,y in zip(r,r[1:])]
    require(len(r) == 4 and len({x['case_id'] for x in r}) == 1 and gaps == [1800,2700,900] and sum(gaps) == 5400, 'VC-01 expected intervals')
    require(len({(x['activity'],y['activity']) for x,y in zip(r,r[1:])}) == 3, 'VC-01 expected edges')
    print('PASS VC-01 completion-only arithmetic and expected adjacent edges.')
    r = read_csv('complete_temporal_log.csv')[0]
    require(seconds(r['timestamp'],r['start_timestamp']) == 900 and seconds(r['start_timestamp'],r['queue_entry']) == 600, 'VC-02')
    print('PASS VC-02 elapsed service and queue wait arithmetic.')
    r = read_csv('paired_lifecycle.csv')
    require(len(r) == 3 and len({(x['case_id'],x['activity'],x['activity_instance_id']) for x in r}) == 1, 'VC-03 occurrence key')
    t = {x['lifecycle']:x['timestamp'] for x in r}
    require(set(t) == {'queue_entry','start','complete'} and seconds(t['complete'],t['start']) == 900 and seconds(t['start'],t['queue_entry']) == 600, 'VC-03')
    print('PASS VC-03 known paired lifecycle fixture (not a pairing algorithm).')
    tree = ET.parse(EX / 'minimal_log.xes'); ns = {'x':'http://www.xes-standard.org/'}
    trace = tree.find('x:trace',ns); evs = trace.findall('x:event',ns)
    require(trace.find('x:string',ns).attrib == {'key':'concept:name','value':'P001'}, 'VC-04 trace scope')
    t = [e.find('x:date',ns).attrib['value'] for e in evs]
    require(len(t) == 2 and [instant(x).isoformat() for x in t] == ['2026-10-01T08:00:00+00:00','2026-10-01T09:15:00+00:00'] and seconds(t[1],t[0]) == 4500, 'VC-04')
    require(sha('minimal_log.xes') == load(EX / 'xes_mapping.example.json')['input_sha256'], 'XES checksum')
    print('PASS VC-04 XML structure, trace scope, source checksum and offset arithmetic (not XES conformance).')
    r = read_csv('validation/vc08_offsets.csv')
    require(instant(r[0]['timestamp']) == instant(r[1]['timestamp']), 'VC-08')
    print('PASS VC-08 equal UTC instants.')
    r = read_csv('validation/vc19_zero_wait.csv')[0]
    require(seconds(r['start_timestamp'],r['queue_entry']) == 0, 'VC-19')
    print('PASS VC-19 observed equal endpoints yield zero.')
    r = read_csv('validation/vc20_case_boundaries.csv')
    pairs = [(x,y) for case in ('P001','P002') for seq in [[v for v in r if v['case_id'] == case]] for x,y in zip(seq,seq[1:])]
    require(len(pairs)==2 and [seconds(y['timestamp'],x['timestamp']) for x,y in pairs]==[3600,4440], 'VC-20')
    print('PASS VC-20 expected within-case intervals only.')
    # Demonstrate two limitations of structural checks using intentionally inconsistent fixture data.
    for name,key in [('vc16_stale_revision','mapping_version'),('vc16_wrong_hash','input_sha256')]:
        f = load(EX / 'validation' / (name+'.json'))
        require(f[key] != f['approval'][key], f'{name} should disagree')
    print('PASS VC-16 fixtures contain mismatched references despite structural acceptance; runtime gate remains unimplemented.')
    print('SUCCESS — design artifact checks only. Remaining VC outcomes require future implementation tests.')

if __name__ == '__main__':
    main()
