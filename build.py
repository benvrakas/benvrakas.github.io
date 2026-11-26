"""Static site builder for benvrakas.github.io.

  python build.py                       # builds content/ -> docs/
  python -m http.server -d docs 8765    # preview at http://localhost:8765

content/projects/*.md : one file per project. Front matter between --- lines (key: value):
  title, years, tags (comma list), areas (comma list: mechanical, electrical, software, printing, fabrication),
  summary, hero (media name), codeart (text shown when no hero), order (number), draft (true/false),
  links ("Label | url ; Label | url"), theme (print | pcb | code | lab | cad; default from first area)
  A section can take its own theme: ## Firmware {: theme=code }
Body is Markdown plus these blocks (media names resolve to docs/media/<slug>/<name>.jpg):
  :::gallery            one "name | caption" per line, closed by ::: (sorted by capture date; dates appended)
  :::video name | caption     muted autoplay loop clip
  :::clip name | caption      clip with controls and sound
  :::youtube VIDEO_ID | caption
content/home.md : front matter (eyebrow, tagline, intro, skills, stats "value|label|Sym ; ...", hero_image)
  plus <!-- section: name --> blocks: experience, about, contact.
"""
import hashlib, html, json, os, re, sys
from datetime import date
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT, OUT = os.path.join(ROOT, 'content'), os.path.join(ROOT, 'docs')
SITE = {'name': 'Ben Vrakas', 'url': 'https://benvrakas.github.io'}
NAV = [('Work', 'index.html#work'), ('Timeline', 'index.html#timeline'), ('Experience', 'index.html#experience'),
       ('About', 'index.html#about'), ('Resume', 'resume.html'), ('Contact', 'index.html#contact')]
RESUME_PDF = 'Ben_Vrakas_Resume.pdf'
AREAS = [('mechanical', 'Mechanical'), ('electrical', 'Electrical'), ('software', 'Software'),
         ('printing', '3D printing'), ('fabrication', 'Fabrication')]
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
# page/section themes: name -> (badge, theme-color)
THEMES = {'print': ('G-CODE', '#100e0c'), 'pcb': ('PCB', '#08110d'), 'code': ('SRC', '#0d1117'),
          'lab': ('LAB', '#0c0d16'), 'cad': ('DWG', '#0a1220')}
AREA_THEME = {'printing': 'print', 'electrical': 'pcb', 'software': 'code', 'mechanical': 'cad', 'fabrication': 'lab'}
SECTION_LETTERS = 'ABCDEFGHJKLMNPRTUVWY'   # drawing section labels skip I, O, Q, S, X, Z
STOP = {'the', 'and', 'a', 'an', 'of', 'for', 'in', 'my', 'to', 'with', 'own'}


def front_matter(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def media(slug, name, thumb=False):
    return f"media/{slug}/{name}{'_t' if thumb else ''}.jpg"


_dates_cache = {}


def dates_for(slug):
    if slug not in _dates_cache:
        p = os.path.join(OUT, 'media', slug, '_dates.json')
        _dates_cache[slug] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    return _dates_cache[slug]


def nice_date(d):
    return f'{MONTHS[int(d[5:7]) - 1]} {d[:4]}' if d else ''


def with_date(cap, d):
    if d and not re.search(r'\b(19|20)\d\d\b', cap or ''):
        return f'{cap} · {nice_date(d)}' if cap else nice_date(d)
    return cap


def blocks(slug, body, prefix):
    dates = dates_for(slug)

    def gallery(m):
        rows = []
        for line in m.group(1).strip().splitlines():
            name, _, cap = (p.strip() for p in line.partition('|'))
            if name:
                rows.append((name, cap, dates.get(name, '')))
        rows.sort(key=lambda r: r[2] or '0000')   # undated (renders/CAD) first, then chronological
        items = []
        for name, cap, d in rows:
            full, th = prefix + media(slug, name), prefix + media(slug, name, True)
            cap = with_date(cap, d)
            alt = html.escape(cap or name.replace('-', ' '))
            items.append(f'<figure><a href="{full}" class="lb" data-cap="{alt}"><img src="{th}" alt="{alt}" loading="lazy"></a>'
                         + (f'<figcaption>{html.escape(cap)}</figcaption>' if cap else '') + '</figure>')
        cls = 'gallery g1' if len(items) == 1 else ('gallery g2' if len(items) in (2, 4) else 'gallery')
        return f'\n<div class="{cls}">' + ''.join(items) + '</div>\n'

    def video(m, controls=False):
        name, cap = m.group(1).strip(), (m.group(2) or '').strip()
        cap = with_date(cap, dates.get(name, ''))
        src = prefix + f'media/{slug}/{name}'
        attrs = 'controls preload="none"' if controls else 'autoplay muted loop playsinline preload="metadata"'
        return (f'\n<figure class="video"><video src="{src}.mp4" poster="{src}.jpg" {attrs}></video>'
                + (f'<figcaption>{html.escape(cap)}</figcaption>' if cap else '') + '</figure>\n')

    def youtube(m):
        vid, cap = m.group(1).strip(), (m.group(2) or '').strip()
        return (f'\n<figure class="yt"><button class="yt-lite" data-id="{vid}" aria-label="Play video: {html.escape(cap)}"'
                f' style="background-image:url(https://i.ytimg.com/vi/{vid}/hqdefault.jpg)"><span></span></button>'
                + (f'<figcaption>{html.escape(cap)}</figcaption>' if cap else '') + '</figure>\n')

    body = re.sub(r'^:::gallery\s*\n(.*?)^:::\s*$', gallery, body, flags=re.S | re.M)
    body = re.sub(r'^:::video\s+([^|\n]+)(?:\|(.*))?$', video, body, flags=re.M)
    body = re.sub(r'^:::clip\s+([^|\n]+)(?:\|(.*))?$', lambda m: video(m, True), body, flags=re.M)
    body = re.sub(r'^:::youtube\s+([^|\n]+)(?:\|(.*))?$', youtube, body, flags=re.M)
    # consecutive youtube figures -> side-by-side row
    body = re.sub(r'((?:\n<figure class="yt">.*?</figure>\n){2,})', lambda m: '\n<div class="ytrow">' + m.group(1).replace('\n', '') + '</div>\n', body)
    return body


def md(text):
    return markdown.markdown(text, extensions=['tables', 'attr_list', 'md_in_html', 'sane_lists', 'toc'])


def theme_of(p):
    t = p.get('theme', '').strip()
    return t if t in THEMES else AREA_THEME.get((p.get('areas') or ['mechanical'])[0], 'cad')


def _plain(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s))


def _words(s, n=2):
    s = re.sub(r'\([^)]*\)', ' ', _plain(s)).lower()
    w = [x.replace('-', '') for x in re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)*', s) if x not in STOP]
    return w[:n] or ['section']


def sec_tag(theme, i, text):
    """The small themed label above each section heading."""
    w = _words(text)
    if theme == 'print':
        return f'<span class="stag">;LAYER:{i} <b>Z{i * 0.2:.2f}</b> ;TYPE:{"-".join(w).upper()}</span>'
    if theme == 'pcb':
        return f'<span class="stag"><b>U{i}</b><i></i>NET_{"_".join(w).upper()}</span>'
    if theme == 'code':
        return f'<span class="stag"><b>def</b> <em>{"_".join(w)}</em>():</span>'
    if theme == 'lab':
        sym = w[0][0].upper() + (w[1][0] if len(w) > 1 else w[0][1:2])
        yr = re.search(r'(19|20)\d\d', _plain(text))
        return f'<span class="stag elem"><sup>{i}</sup><b>{sym}</b><sub>{yr.group(0) if yr else w[0][:9]}</sub></span>'
    L = SECTION_LETTERS[(i - 1) % len(SECTION_LETTERS)]
    return f'<span class="stag">SECTION <b>{L}–{L}</b></span>'


def wrap_sections(content, pt):
    """Split rendered HTML at each h2 into <section class="psec t-x">; a section's own theme (theme="x") overrides the page's."""
    out, i = [], 0
    for part in re.split(r'(?=<h2[\s>])', content):
        if not part.strip():
            continue
        m = re.match(r'<h2([^>]*)>(.*?)</h2>', part, re.S)
        if not m:
            out.append(f'<section class="psec t-{pt}">{part}</section>')
            continue
        i += 1
        attrs, text = m.group(1), m.group(2)
        tm = re.search(r'\stheme="(\w+)"', attrs)
        th = tm.group(1) if tm and tm.group(1) in THEMES else pt
        idm = re.search(r'\sid="([^"]+)"', attrs)
        sid = f' id="{idm.group(1)}"' if idm else ''
        own = ' own' if th != pt else ''
        out.append(f'<section class="psec t-{th}{own}"{sid}><div class="shead">{sec_tag(th, i, text)}<h2>{text}</h2></div>'
                   f'{part[m.end():]}</section>')
    return ''.join(out)


def viz(theme, title='', years='', tags=(), slug='', seed=7):
    return (f'<div class="viz" data-viz="{theme}" data-title="{html.escape(title)}" data-years="{html.escape(years)}" '
            f'data-tags="{html.escape("|".join(tags))}" data-slug="{slug}" data-seed="{seed}" aria-hidden="true"></div>')


def page(title, body, prefix='', desc='', og_image='', active='', page_path='', color='#0d0f12'):
    nav = ''.join(f'<a href="{prefix + u}">{n}</a>' for n, u in NAV)
    nav += '<a class="gh" href="https://github.com/benvrakas">GitHub ↗</a>'
    og = f'<meta property="og:image" content="{SITE["url"]}/{og_image}">' if og_image else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="{color}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ben Vrakas">
<meta property="og:url" content="{SITE["url"]}/{html.escape(page_path)}">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
{og}
<link rel="icon" href="{prefix}favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}style.css">
<link rel="stylesheet" href="{prefix}themes.css">
</head>
<body class="{active}">
<header class="top"><div class="wrap"><a class="brand" href="{prefix}index.html"><span class="mark">BV</span>Ben Vrakas</a><nav>{nav}</nav></div></header>
<main>
{body}
</main>
<footer class="foot"><div class="wrap"><span>© {date.today().year} Ben Vrakas · V-Labs</span>
<span><a href="https://github.com/benvrakas">GitHub</a> · <a href="https://www.printables.com/@VLabs_256532">Printables</a> · <a href="https://www.thingiverse.com/benvrakas/designs">Thingiverse</a> · <a href="https://ficsit.app/user/benvrakas">ficsit.app</a> · <a href="https://www.youtube.com/channel/UC1nUGgfhgWf4mYUwQ9nH5FQ">YouTube</a></span></div></footer>
<div id="lightbox" hidden><button class="lbx" aria-label="Close">×</button><button class="lbp" aria-label="Previous">‹</button><figure><img alt=""><figcaption></figcaption></figure><button class="lbn" aria-label="Next">›</button></div>
<script src="{prefix}site.js" defer></script>
<script src="{prefix}viz.js" defer></script>
</body>
</html>
'''


def load_projects():
    projects = []
    pdir = os.path.join(CONTENT, 'projects')
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith('.md'):
            continue
        meta, body = front_matter(open(os.path.join(pdir, fn), encoding='utf-8').read())
        meta['slug'] = fn[:-3]
        meta['body'] = body
        meta['tags'] = [t.strip() for t in meta.get('tags', '').split(',') if t.strip()]
        meta['areas'] = [t.strip().lower() for t in meta.get('areas', '').split(',') if t.strip()]
        meta['order'] = float(meta.get('order', 99))
        yrs = re.findall(r'(19|20)(\d\d)', meta.get('years', ''))
        meta['y0'] = int(''.join(yrs[0])) if yrs else 0
        meta['y1'] = int(''.join(yrs[-1])) if yrs else 0
        if 'ongoing' in meta.get('years', '').lower() or 'progress' in meta.get('years', '').lower():
            meta['y1'] = date.today().year
        if meta.get('draft', 'false').lower() != 'true' or '--drafts' in sys.argv:
            projects.append(meta)
    return sorted(projects, key=lambda p: p['order'])


def chips(tags, cls='chips'):
    return f'<ul class="{cls}">' + ''.join(f'<li>{html.escape(t)}</li>' for t in tags) + '</ul>'


def links_html(s):
    out = []
    for part in filter(None, (x.strip() for x in (s or '').split(';'))):
        label, _, url = (x.strip() for x in part.partition('|'))
        out.append(f'<a class="btn" href="{html.escape(url)}">{html.escape(label)} ↗</a>')
    return '<div class="links">' + ''.join(out) + '</div>' if out else ''


def build_project(p, projects):
    slug, pre = p['slug'], '../'
    t = theme_of(p)
    content = md(blocks(slug, p['body'], pre))
    toc = re.findall(r'<h2[^>]*\bid="([^"]+)"[^>]*>(.*?)</h2>', content)
    content = wrap_sections(content, t)
    i = projects.index(p)
    prev, nxt = (projects[i - 1] if i else None), (projects[i + 1] if i + 1 < len(projects) else None)
    hero = (f'<div class="phero"><img src="{pre}{media(slug, p["hero"])}" alt="{html.escape(p["title"])}"></div>'
            if p.get('hero') else '')
    side = '<aside class="side"><div class="sticky">'
    if toc:
        side += '<p class="sh2">On this page</p><ul class="toc"><li><a href="#top">Overview</a></li>' + ''.join(
            f'<li><a href="#{a}">{t}</a></li>' for a, t in toc) + '</ul>'
    side += '<p class="sh2">All projects</p><ul class="plist">' + ''.join(
        f'<li{" class=cur" if q is p else ""}><a href="{q["slug"]}.html"><i class="tdot t-{theme_of(q)}"></i><span>{html.escape(q["title"])}</span>'
        f'<em>{q["y0"] or ""}</em></a></li>' for q in projects) + '</ul></div></aside>'
    pager = '<nav class="pager">' + (f'<a href="{prev["slug"]}.html">← {html.escape(prev["title"])}</a>' if prev else '<span></span>') \
        + (f'<a href="{nxt["slug"]}.html">{html.escape(nxt["title"])} →</a>' if nxt else '') + '</nav>'
    body = f'''<div class="wrap playout" id="top">
{side}
<article class="project">
<header class="phead"><div class="phtext">
<a class="back" href="../index.html#work">← All work</a>
<p class="eyebrow">{html.escape(p.get("years", ""))} <span class="tbadge">{THEMES[t][0]}</span></p>
<h1>{html.escape(p["title"])}</h1>
<p class="lede">{html.escape(p.get("summary", ""))}</p>
{chips(p["tags"])}
{links_html(p.get("links"))}
</div>{viz(t, p["title"], p.get("years", ""), p["tags"][:3], slug, int(p["order"] * 7) + 3)}</header>
{hero}
<div class="prose">{content}</div>
{pager}
</article>
</div>'''
    og = media(slug, p['hero']) if p.get('hero') else ''
    return page(f'{p["title"]} · Ben Vrakas', body, pre, p.get('summary', ''), og, f'proj t-{t}', f'projects/{slug}.html', THEMES[t][1])


def card(p):
    slug = p['slug']
    img = (f'<img src="{media(slug, p["hero"], True)}" alt="" loading="lazy">' if p.get('hero')
           else f'<div class="codeart"><span>{html.escape(p.get("codeart", "</>"))}</span></div>')
    t = theme_of(p)
    return f'''<a class="card t-{t}" href="projects/{slug}.html" data-areas="{' '.join(p['areas'])}">
<div class="thumb">{img}<span class="tbadge">{THEMES[t][0]}</span></div>
<div class="cbody"><p class="eyebrow">{html.escape(p.get("years", ""))}</p><h3>{html.escape(p["title"])}</h3>
<p>{html.escape(p.get("summary", ""))}</p>{chips(p["tags"][:4])}</div></a>'''


def build_home(projects):
    meta, body = front_matter(open(os.path.join(CONTENT, 'home.md'), encoding='utf-8').read())
    sections = re.split(r'^<!--\s*section:\s*(\w+)\s*-->\s*$', body, flags=re.M)
    sec = {sections[i]: sections[i + 1] for i in range(1, len(sections), 2)}
    stats = ''
    for n, st in enumerate((x for x in meta.get('stats', '').split(';') if x.strip()), 1):
        v, l, sym = ([x.strip() for x in st.split('|')] + ['', ''])[:3]
        stats += (f'<div class="stat"><sup>{n:02d}</sup><i>{html.escape(sym)}</i>'
                  f'<b>{html.escape(v)}</b><span>{html.escape(l)}</span></div>')
    used = {a for p in projects for a in p['areas']}
    filt = '<div class="filters" role="group" aria-label="Filter projects"><button class="on" data-f="all">All</button>' + ''.join(
        f'<button class="t-{AREA_THEME[k]}" data-f="{k}">{v}</button>' for k, v in AREAS if k in used) + '</div>'
    grid = '<div class="grid">' + ''.join(card(p) for p in projects) + '</div>'
    tl = sorted(projects, key=lambda p: (-p['y1'], -p['y0']))
    timeline = '<ol class="timeline">' + ''.join(
        f'<li class="t-{theme_of(p)}" data-areas="{" ".join(p["areas"])}"><a href="projects/{p["slug"]}.html"><span class="ty">{html.escape(p.get("years", ""))}</span>'
        f'<span class="tt">{html.escape(p["title"])}</span><span class="ts">{html.escape(p.get("summary", ""))}</span></a></li>'
        for p in tl) + '</ol>'
    hero_img = meta.get('hero_image', '')
    exp = re.sub(r'<h3>(.*?)</h3>', lambda m: f'<h3><code class="hash">{hashlib.sha1(_plain(m.group(1)).encode()).hexdigest()[:7]}</code>'
                 f'<span>{m.group(1)}</span></h3>', md(sec.get('experience', '')))

    def head(title, tag):
        return f'<div class="shrow"><h2 class="sh">{title}</h2><span class="stag">{tag}</span></div>'
    out = f'''<section class="hero wrap">
<div class="htext">
<p class="eyebrow">{html.escape(meta.get("eyebrow", ""))}</p>
<h1>{meta.get("tagline", "")}</h1>
<p class="lede">{html.escape(meta.get("intro", ""))}</p>
{chips([t.strip() for t in meta.get("skills", "").split(",") if t.strip()])}
</div>
{f'<div class="himg"><img src="{hero_img}" alt=""></div>' if hero_img else ''}
</section>
<section class="wrap t-lab hstats"><div class="stats">{stats}</div></section>
<section id="work" class="wrap"><div class="shrow"><h2 class="sh">Selected work</h2>{filt}</div>{grid}</section>
<section id="timeline" class="wrap hsec t-print">{head("Timeline", f";LAYER_COUNT:{len(tl)}")}{timeline}</section>
<section id="experience" class="wrap narrow hsec t-code prose">{head("Experience", '$ git log --author="Ben Vrakas"')}<div class="gitlog">{exp}</div></section>
<section id="about" class="wrap narrow hsec t-lab prose">{head("About", '<span class="elem"><sup>23</sup><b>V</b><sub>V-Labs</sub></span>')}
<div class="about">{viz("lab", seed=23)}{md(sec.get("about", ""))}</div></section>
<section id="contact" class="wrap narrow hsec t-pcb prose pinout">{head("Contact & elsewhere", "<b>J1</b><i></i>NET_CONTACT")}{md(sec.get("contact", ""))}</section>'''
    return page('Ben Vrakas · Mechanical design, electronics & software', out, '', meta.get('intro', ''), hero_img, 'home', '')


def build_resume():
    """docs/resume.html: a paper-style page that prints to one Letter page; the PDF is made by make_pdf()."""
    meta, body = front_matter(open(os.path.join(CONTENT, 'resume.md'), encoding='utf-8').read())
    contact = md(meta.get('contact', '')).replace('<p>', '').replace('</p>', '').replace(' | ', ' <i>·</i> ')
    sheet = f'''<div class="paper">
<header class="rhead"><h1>{html.escape(meta.get("name", ""))}</h1><p class="rtitle">{html.escape(meta.get("title", ""))}</p>
<p class="rcontact">{contact}</p></header>
{md(body)}
</div>'''
    tools = (f'<div class="rtools wrap"><a class="btn" href="{RESUME_PDF}">Download PDF ↓</a>'
             f'<a class="btn" href="index.html#work">See the projects →</a></div>')
    out = page('Resume · Ben Vrakas', tools + sheet, '', 'Resume of Ben Vrakas', 'media/carbon-3d-pc/2024-outdoor.jpg', 'resume', 'resume.html')
    out = out.replace('<link rel="stylesheet" href="style.css">',
                      '<link rel="stylesheet" href="style.css">\n<link rel="stylesheet" href="resume.css">')
    open(os.path.join(OUT, 'resume.html'), 'w', encoding='utf-8').write(out)


def make_pdf():
    """Print docs/resume.html to docs/<RESUME_PDF> with headless Chrome/Edge (if installed)."""
    import subprocess, pathlib
    for exe in [r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe']:
        if os.path.exists(exe):
            src = pathlib.Path(OUT, 'resume.html').resolve().as_uri()
            dst = os.path.join(OUT, RESUME_PDF)
            subprocess.run([exe, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=4000',
                            f'--print-to-pdf={dst}', src], capture_output=True, timeout=120)
            print('pdf:', dst if os.path.exists(dst) else 'FAILED', exe)
            return
    print('pdf: no Chrome/Edge found')


def main():
    projects = load_projects()
    build_resume()
    if '--pdf' in sys.argv:
        make_pdf()
    os.makedirs(os.path.join(OUT, 'projects'), exist_ok=True)
    for p in projects:
        open(os.path.join(OUT, 'projects', p['slug'] + '.html'), 'w', encoding='utf-8').write(build_project(p, projects))
        names = re.findall(r'^(?!:::)\s*([a-z0-9-]+)\s*\|', p['body'], re.M) + re.findall(r'^:::(?:video|clip)\s+([a-z0-9-]+)', p['body'], re.M)
        for m in names + ([p['hero']] if p.get('hero') else []):
            if not os.path.exists(os.path.join(OUT, media(p['slug'], m))):
                print(f'  missing media: {p["slug"]}/{m}')
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(build_home(projects))
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print(f'built {len(projects)} projects -> docs/')


if __name__ == '__main__':
    main()
