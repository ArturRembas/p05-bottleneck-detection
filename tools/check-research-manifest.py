"""Read-only research baseline checksum audit; absent historical logs are reported, not fabricated."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifest = json.loads((root / 'results/audit/baseline_v0.1.json').read_text())
ok, missing, altered = [], [], []
for relative, expected in manifest['files'].items():
    p = root / relative
    if not p.exists():
        missing.append(relative)
    elif hashlib.sha256(p.read_bytes()).hexdigest() != expected:
        altered.append(relative)
    else:
        ok.append(relative)
print(json.dumps({'matching': len(ok), 'missing': missing, 'mismatch': altered}, indent=2))
if altered:
    sys.exit(1)
