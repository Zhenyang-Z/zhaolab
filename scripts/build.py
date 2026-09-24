"""Build the complete static site using only the Python standard library."""
from pathlib import Path
import json
import re
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'

def data(name):
    return json.loads((ROOT / 'data' / f'{name}.json').read_text(encoding='utf-8'))

def image(item, alt='', cls='', eager=False):
    return f'<img src="{escape(item["src"])}" width="{item["width"]}" height="{item["height"]}" alt="{escape(alt)}" class="{cls}" loading="{"eager" if eager else "lazy"}">'

pages, contact = data('pages'), data('contact')
phone_uri = re.sub(r'[^+0-9]', '', contact['phone'])
if phone_uri.startswith('+860'):
    phone_uri = '+86' + phone_uri[4:]  # Omit the domestic trunk prefix in international dialing.
routes = [('index.html', 'Home'), ('research.html', 'Research'), ('publications.html', 'Publications'), ('team.html', 'Team'), ('group-activities.html', 'Group activities')]

def shell(filename, title, body):
    links = ''.join(f'<a href="{url}"'+(' aria-current="page"' if url == filename else '')+f'>{label}</a>' for url, label in routes)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} — Zhao lab</title><meta name="description" content="Zhao lab at the University of Chinese Academy of Sciences. Research, publications, team and group activities.">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="site.css"><script src="site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><a class="brand" href="index.html" aria-label="Zhao lab home"><img src="assets/logo.png" alt="Zhao lab" width="753" height="217"></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Menu <span aria-hidden="true">☰</span></button><nav id="navigation" aria-label="Main navigation">{links}</nav></header>
<main id="main">{body}</main><footer><a href="index.html">Zhao lab</a><span>University of Chinese Academy of Sciences</span><a href="team.html#contact">Contact &amp; opportunities</a></footer></body></html>'''

def hero(title, item, home=False):
    heading = 'Development of<br>Novel Reaction Chemistry' if home else escape(title)
    return f'<section class="hero {"home-hero" if home else ""}">{image(item, "", eager=True)}<h1>{heading}</h1></section>'

def write(filename, title, body):
    (OUT / filename).write_text(shell(filename, title, body), encoding='utf-8')

home = pages['home']
write('index.html', 'Home', hero(home['title'], home['images'][0], True) + '<section class="content home-intro">'+home['intro_html']+'<div class="campus-gallery">'+''.join(image(x, ['UCAS campus sign', 'Campus building at dusk', 'Campus landscape at dusk'][i]) for i,x in enumerate(home['images'][1:]))+'</div></section>')
research = pages['research']
write('research.html', 'Research', hero('Research', research['images'][0]) + '<section class="content research-intro">'+research['intro_html']+'</section>')
pubs = hero('Publications', pages['publications']['hero']) + '<section class="content publications">'
period = None
for rec in data('publications'):
    if rec['period'] != period:
        period=rec['period']; pubs+=f'<h2>{escape(period)}:</h2>'
    pubs+=f'<article class="publication" id="publication-{rec["number"]}">'+rec['content_html']
    if rec.get('figure'): pubs+=image(rec['figure'], f'Graphical abstract for publication {rec["number"]}', 'publication-figure')
    pubs+='</article>'
write('publications.html', 'Publications', pubs+'</section>')
members=data('members'); pi=members[0]
team=hero('The group',pages['team']['hero'])+'<section class="content team-content"><div class="principal"><div>'+image(pi['image'], pi['name'], 'pi-photo')
team+=f'''<address id="contact"><h2>{escape(contact['name'])}</h2><p>{escape(contact['institution'])}<br>{escape(contact['address'])}</p><a href="mailto:{contact['email']}">{contact['email']}</a><br><a href="tel:{phone_uri}">{contact['phone']}</a><p id="join">Contact for Job Applicants:<br><a href="mailto:{contact['application_email']}">{contact['application_email']}</a></p></address></div><div class="biography">{pi['biography_html']}</div></div><div class="members">'''
for m in members[1:]:
    team+='<article class="member">'+image(m['image'],m['name'])+f'<h2>{escape(m["name"])}</h2><p>{escape(m["role"])}</p><p>{escape(m["education"])}</p><a href="mailto:{escape(m["email"])}">{escape(m["email"])}</a></article>'
write('team.html','Team',team+'</div></section>')
activities=pages['activities']
write('group-activities.html','Group activities',hero(activities['title'],activities['images'][0])+'<section class="content activities">'+activities['intro_html']+'<div class="activity-gallery">'+''.join(image(x,f'Group activity photograph {i+1}') for i,x in enumerate(activities['images'][1:]))+'</div></section>')
# Preserve old Squarespace route names for migrated bookmarks and internal references.
for old,new in [('new-page-2','index.html'),('new-page-1','research.html'),('new-page','team.html'),('publications','publications.html'),('group-activities','group-activities.html')]:
    folder=OUT/old;folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../{new}"><title>Zhao lab</title><a href="../{new}">Continue to Zhao lab</a></html>',encoding='utf-8')
(OUT/'.nojekyll').touch()
print('Built 5 pages and 5 legacy route redirects in dist/.')
