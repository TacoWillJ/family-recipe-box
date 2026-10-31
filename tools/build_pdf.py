"""Build the downloadable cookbook PDFs.

    python3 tools/build_pdf.py

Writes cookbook.pdf (text only) and cookbook-with-photos.pdf at the repo root.
Recipes are grouped by category (in the order categories first appear), then by number.
Rerun after every batch so the downloads stay current.
"""
import json, os, html, base64, io, datetime, subprocess, sys, tempfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, 'recipes.json')))
recipes = d['recipes']
e = lambda s: html.escape(str(s or ''))

cats = []
for r in recipes:
    if r['category'] not in cats:
        cats.append(r['category'])
# keep non-food last
if 'Crafts & Other' in cats:
    cats.remove('Crafts & Other'); cats.append('Crafts & Other')
by_cat = {c: sorted([r for r in recipes if r['category'] == c], key=lambda r: r['id']) for c in cats}

def img_data(src, maxpx=750):
    p = os.path.join(ROOT, src)
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert('RGB'); im.thumbnail((maxpx, maxpx))
    b = io.BytesIO(); im.save(b, "JPEG", quality=62)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

CSS = """
@page { size: letter; margin: 0.6in 0.65in; @bottom-center { content: counter(page); } }
body { font-family: Georgia, 'Times New Roman', serif; color: #1d2118; font-size: 11pt; line-height: 1.45; }
h1, h2, h3 { font-weight: normal; margin: 0; }
.cover { height: 9.2in; display: flex; flex-direction: column; justify-content: center; text-align: center; break-after: page; }
.cover h1 { font-size: 40pt; }
.cover p { color: #555; margin: 10px 0 0; }
.cover img { max-width: 5.5in; max-height: 3.5in; margin: 0 auto 28px; border-radius: 4px; }
.toc { break-after: page; }
.toc h2 { font-size: 22pt; margin-bottom: 12px; }
.toc .cat { font-size: 13pt; margin: 14px 0 4px; color: #a8455a; }
.toc ul { columns: 2; column-gap: 28px; list-style: none; padding: 0; margin: 0; font-size: 9.5pt; }
.toc li { break-inside: avoid; padding: 1px 0; }
.toc a { color: inherit; text-decoration: none; }
.toc .no { font-family: 'Courier New', monospace; color: #a8455a; margin-right: 6px; }
.section { break-before: page; font-size: 26pt; color: #a8455a; border-bottom: 2px solid #a8455a; padding-bottom: 6px; margin-bottom: 18px; }
.recipe { break-inside: avoid-page; margin-bottom: 26px; padding-bottom: 18px; border-bottom: 1px dashed #bbb; }
.recipe.photos { break-before: page; break-inside: auto; border: 0; }
.recipe .no { font-family: 'Courier New', monospace; font-size: 9pt; color: #a8455a; letter-spacing: .05em; }
.recipe h3 { font-size: 17pt; margin: 2px 0 4px; }
.facts { font-size: 9.5pt; color: #555; margin-bottom: 8px; }
.cols { display: grid; grid-template-columns: 2fr 3fr; gap: 20px; }
h4 { font: bold 8.5pt Arial, sans-serif; letter-spacing: .1em; text-transform: uppercase; color: #6f8a5e; margin: 0 0 4px; }
ul.ing { list-style: none; padding: 0; margin: 0; font-size: 10pt; }
ul.ing li { padding: 2px 0; border-bottom: 1px dotted #ccc; }
ol { margin: 0; padding-left: 1.3em; font-size: 10pt; }
ol li { margin-bottom: 3px; }
.notes { font-size: 9pt; color: #444; margin-top: 8px; }
.notes p { margin: 2px 0; }
figure { margin: 12px 0 0; break-inside: avoid; text-align: center; }
figure img { max-width: 100%; max-height: 4.2in; border: 1px solid #ccc; }
figcaption { font-size: 8.5pt; color: #666; }
"""

def build(photos):
    out = ['<!doctype html><html><head><meta charset="utf-8"><title>Family Recipe Box</title><style>', CSS, '</style></head><body>']
    cover = img_data('img/box.jpg', 1400)
    out.append('<div class="cover">' + (f'<img src="{cover}">' if cover else '') +
               '<h1>Family Recipe Box</h1><p>Grandma Sharp\'s recipe box, typed up' +
               (', with photos of the original cards' if photos else '') + '.</p>' +
               f'<p>{len(recipes)} recipes &middot; {datetime.date.today():%B %-d, %Y}</p>' +
               '<p style="font-size:9pt">The newest version is always at tacowillj.github.io/family-recipe-box</p></div>')
    out.append('<div class="toc"><h2>Contents</h2>')
    for c in cats:
        out.append(f'<div class="cat">{e(c)}</div><ul>')
        for r in by_cat[c]:
            out.append(f'<li><a href="#r{r["id"]}"><span class="no">{r["id"]}</span>{e(r["title"])}</a></li>')
        out.append('</ul>')
    out.append('</div>')
    for c in cats:
        out.append(f'<h2 class="section">{e(c)}</h2>')
        for i, r in enumerate(by_cat[c]):
            facts = []
            if r.get('contributor'): facts.append(f'From <b>{e(r["contributor"])}</b>')
            if r.get('yield'): facts.append(f'Makes <b>{e(r["yield"])}</b>')
            if r.get('time'): facts.append(e(r['time']))
            cls = 'recipe photos' if photos and r['photos'] and i > 0 else 'recipe'
            out.append(f'<div class="{cls}" id="r{r["id"]}"><div class="no">No. {r["id"]}</div><h3>{e(r["title"])}</h3>')
            if facts: out.append('<div class="facts">' + ' &middot; '.join(facts) + '</div>')
            out.append('<div class="cols"><div><h4>Ingredients</h4><ul class="ing">' +
                       ''.join(f'<li>{e(x)}</li>' for x in r['ingredients']) + '</ul></div>')
            out.append('<div><h4>Directions</h4><ol>' + ''.join(f'<li>{e(x)}</li>' for x in r['steps']) + '</ol></div></div>')
            if r.get('notes'):
                out.append('<div class="notes">' + ''.join(f'<p>&bull; {e(x)}</p>' for x in r['notes']) + '</div>')
            if photos:
                for p in r['photos']:
                    src = img_data(p['src'])
                    if src: out.append(f'<figure><img src="{src}"><figcaption>{e(p["label"])}</figcaption></figure>')
            out.append('</div>')
    out.append('</body></html>')
    return ''.join(out)

JS = """
const { chromium } = require('playwright');
(async () => {
  const [src, dst] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src, { waitUntil: 'load' });
  await p.pdf({ path: dst, format: 'Letter', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888">Family Recipe Box &middot; <span class="pageNumber"></span></div>',
    margin: { top: '0.6in', bottom: '0.7in', left: '0.65in', right: '0.65in' } });
  await b.close();
})();
"""

with tempfile.TemporaryDirectory() as tmp:
    js = os.path.join(tmp, 'pdf.js'); open(js, 'w').write(JS)
    for photos, name in [(False, 'cookbook.pdf'), (True, 'cookbook-with-photos.pdf')]:
        h = os.path.join(tmp, name + '.html'); open(h, 'w').write(build(photos))
        subprocess.run(['node', js, h, os.path.join(ROOT, name)], check=True)
        print(name, round(os.path.getsize(os.path.join(ROOT, name)) / 1e6, 1), 'MB')
