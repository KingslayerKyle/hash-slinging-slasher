"""Do a name's hash bytes appear in the decompressed zones?  Evidence for assets a capture did not load.

    python contrib/ff_id_scan.py --names logs/mw7_minimap_names.csv --glob "*x01*" --root "<install>/cod26" --oodle "<install>/oo2core_8_win64.dll"

A snapshot only holds what was loaded when it was taken. An image a map uses is still referred to by id
inside that map's zone, so finding the id's bytes there is evidence the name is real even when the capture
cannot prove it. Matches the low 7 bytes, because the top bit of a stored id may carry a flag.
"""
import argparse
import collections
import csv
import ctypes
import glob
import importlib.util
import os
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--names', required=True)
parser.add_argument('--root', required=True)
parser.add_argument('--oodle', required=True)
parser.add_argument('--glob', default='*x01*')
parser.add_argument('--filter', default='x01|tumen_grid|deploy_map|rew_tumen_01_01')
parser.add_argument('--harvester', default='scripts/contributed/harvest_mwiii_20261013-162139.py')
options = parser.parse_args()

spec = importlib.util.spec_from_file_location('harvester', options.harvester)
harvester = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harvester)

wanted = {}
states = {}
for row in csv.DictReader(open(options.names, encoding='utf-8')):
    if re.search(options.filter, row['name']):
        key = int(row['hash'], 16)
        wanted[key.to_bytes(8, 'little')[:7]] = row['name']
        states[row['name']] = row['state']
print('names checked', len(wanted), file=sys.stderr)

found = collections.defaultdict(set)
current = [None]
def scan(data):
    for needle, name in wanted.items():
        if data.find(needle) >= 0:
            found[name].add(current[0])
harvester.take = scan

decoder = harvester.oodle(options.oodle)
files = sorted(glob.glob(os.path.join(options.root, options.glob + '.ff')))
print('files', len(files), file=sys.stderr)
for path in files:
    current[0] = os.path.basename(path)
    harvester.run_blocks(path, decoder)

for name in sorted(wanted.values()):
    where = sorted(found.get(name, ()))
    print('%-3s %-34s %s %s' % ('YES' if where else 'no', states[name][:34], name, where[:2]))
print('found', sum(1 for n in wanted.values() if n in found), 'of', len(wanted))
