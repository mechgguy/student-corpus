from pathlib import Path
import json

from src.cv_pipeline.contact_extractor import extract_contacts

p = Path('data/output/candidates.json')
if not p.exists():
    print('Original output not found:', p)
    raise SystemExit(1)

recs = json.loads(p.read_text(encoding='utf-8'))
changed = []
for r in recs:
    raw = r.get('raw_text', '') or ''
    contact = extract_contacts(raw)
    contact_name = contact.get('name')
    old_name = r.get('name')
    if contact_name and contact_name != old_name:
        r['name'] = contact_name
        changed.append((r.get('filename'), old_name, contact_name))

out = Path('data/output/candidates_fixed.json')
out.write_text(json.dumps(recs, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Wrote {out}. Updated {len(changed)} records.')
if changed:
    print('\nChanges:')
    for fn, old, new in changed:
        print(f'  {fn}: {old!r} -> {new!r}')
else:
    print('  (no changes)')
