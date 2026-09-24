"""Check local HTML references, anchors, data completeness and offline assets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'dist'
class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.refs=[]; self.ids=set(); self.h1=0
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        if tag=='h1': self.h1+=1
        for attr in ['href','src']:
            if a.get(attr): self.refs.append((tag,attr,a[attr]))

docs={p:Document(p) for p in SITE.rglob('*.html')}
errors=[]; external=set(); total=0
for path,doc in docs.items():
    if path.parent==SITE and doc.h1!=1: errors.append(f'{path.name}: expected one h1')
    for tag,attr,ref in doc.refs:
        u=urlsplit(ref)
        if u.scheme in ('http','https'):
            external.add(ref)
            if attr=='src' or tag=='link': errors.append(f'External runtime asset: {ref}')
            continue
        if u.scheme in ('mailto','tel','data'): continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if target.is_dir(): target=target/'index.html'
        total+=1
        if not target.exists(): errors.append(f'{path.name}: missing {ref}')
        elif u.fragment and target in docs and unquote(u.fragment) not in docs[target].ids:
            errors.append(f'{path.name}: missing anchor {ref}')
    text=path.read_text(encoding='utf-8')
    for marker in ['cid:', 'Edit Page', 'stripe.com', 'sqs-frontend', 'data-controller']:
        if marker in text: errors.append(f'{path.name}: leftover export marker {marker}')
pubs=json.loads((ROOT/'data/publications.json').read_text(encoding='utf-8'))
members=json.loads((ROOT/'data/members.json').read_text(encoding='utf-8'))
assert len({p['number'] for p in pubs})==len(pubs), 'Duplicate publication numbers'
assert len({m['name'] for m in members})==len(members), 'Duplicate members'
print(f'{len(docs)} HTML files; {total} local references checked; {len(pubs)} publications; {len(members)} members.')
print(f'{len(external)} external publication links preserved (availability not tested).')
if errors:
    print('\n'.join(errors)); raise SystemExit(1)
print('PASS: local links, image paths, anchors, heading counts and offline resource checks.')
