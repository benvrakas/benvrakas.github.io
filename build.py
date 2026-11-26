"""Static site builder for benvrakas.github.io.

  python build.py            # builds content/ -> docs/
  python -m http.server -d docs 8000   # preview at http://localhost:8000

content/projects/*.md : one file per project. Front matter between --- lines (key: value).
  title, years, tags (comma list), summary, hero (media name), order (number), draft (true/false),
  links ("Label | url ; Label | url")
Body is Markdown plus these blocks (media names resolve to docs/media/<slug>/<name>.jpg):
  :::gallery            one "name | caption" per line, closed by :::
  :::video name | caption
  :::youtube VIDEO_ID | caption
content/home.md : front matter (tagline, intro) + Markdown sections for the home page.
"""
import html, os, re, sys
from datetime import date
import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT, OUT = os.path.join(ROOT, 'content'), os.path.join(ROOT, 'docs')
SITE = {'name': 'Ben Vrakas', 'url': 'https://benvrakas.github.io'}
NAV = [('Work', 'index.html#work'), ('Experience', 'index.html#experience'), ('About', 'index.html#about'),
       ('GitHub', 'https://github.com/benvrakas')]


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


def blocks(slug, body, prefix):
    def gallery(m):
        items = []
        for line in m.group(1).strip().splitlines():
            name, _, cap = (p.strip() for p in line.partition('|'))
            if not name:
                continue
            full, th = prefix + media(slug, name), prefix + media(slug, name, True)
            alt = html.escape(cap or name.replace('-', ' '))
            items.append(f'<figure><a href="{full}" class="lb"><img src="{th}" alt="{alt}" loading="lazy"></a>'
                         + (f'<figcaption>{html.escape(cap)}</figcaption>' if cap else '') + '</figure>')
        cls = 'gallery g1' if len(items) == 1 else ('gallery g2' if len(items) in (2, 4) else 'gallery')
        return f'\n<div class="{cls}">' + ''.join(items) + '</div>\n'

    def video(m):
        name, cap = m.group(1).strip(), (m.group(2) or '').strip()
        src = prefix + f'media/{slug}/{name}'
        return (f'\n<figure class="video"><video src="{src}.mp4" poster="{src}.jpg" autoplay muted loop playsinline'
                f' preload="metadata"></video>' + (f'<figcaption>{html.escape(cap)}</figcaption>' if cap else '')
                + '</figure>\n')

    def youtube(m):
        vid, cap = m.group(1).strip(), (m.group(2) or '').strip()
        return (f'\n<figure class="yt"><button class="yt-lite" data-id="{vid}" aria-label="Play video: {html.escape(cap)}"'
                f' style="background-image:url(https://i.ytimg.com/vi/{vid}/hqdefault.jpg)"><span></span></button>'
                + (f'<figcaption>{html.escape(cap)}</figcaption>' if cap else '') + '</figure>\n')

    body = re.sub(r'^:::gallery\s*\n(.*?)^:::\s*$', gallery, body, flags=re.S | re.M)
    body = re.sub(r'^:::video\s+([^|\n]+)(?:\|(.*))?$', video, body, flags=re.M)
    body = re.sub(r'^:::youtube\s+([^|\n]+)(?:\|(.*))?$', youtube, body, flags=re.M)
    return body


def md(text):
    return markdown.markdown(text, extensions=['tables', 'attr_list', 'md_in_html', 'sane_lists'])


def page(title, body, prefix='', desc='', og_image=''):
    nav = ''.join(f'<a href="{u if u.startswith("http") else prefix + u}">{n}</a>' for n, u in NAV)
    og = f'<meta property="og:image" content="{SITE["url"]}/{og_image}">' if og_image else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
{og}
<link rel="icon" href="{prefix}favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
<header class="top"><div class="wrap"><a class="brand" href="{prefix}index.html"><span class="mark">BV</span>Ben Vrakas</a><nav>{nav}</nav></div></header>
<main>
{body}
</main>
<footer class="foot"><div class="wrap"><span>© {date.today().year} Ben Vrakas</span>
<span><a href="https://github.com/benvrakas">GitHub</a> · <a href="https://www.printables.com/@VLabs_256532">Printables</a> · <a href="https://www.thingiverse.com/benvrakas/designs">Thingiverse</a></span></div></footer>
<div id="lightbox" hidden><img alt=""><button aria-label="Close">×</button></div>
<script src="{prefix}site.js" defer></script>
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
        meta['order'] = float(meta.get('order', 99))
        if meta.get('draft', 'false').lower() != 'true' or '--drafts' in sys.argv:
            projects.append(meta)
    return sorted(projects, key=lambda p: p['order'])


def chips(tags):
    return '<ul class="chips">' + ''.join(f'<li>{html.escape(t)}</li>' for t in tags) + '</ul>'


def links_html(s):
    out = []
    for part in filter(None, (x.strip() for x in (s or '').split(';'))):
        label, _, url = (x.strip() for x in part.partition('|'))
        out.append(f'<a class="btn" href="{html.escape(url)}">{html.escape(label)} ↗</a>')
    return '<div class="links">' + ''.join(out) + '</div>' if out else ''


def build_project(p, prev, nxt):
    slug, pre = p['slug'], '../'
    hero = ''
    if p.get('hero'):
        hero = f'<div class="phero"><img src="{pre}{media(slug, p["hero"])}" alt="{html.escape(p["title"])}"></div>'
    pager = '<nav class="pager">' + (f'<a href="{prev["slug"]}.html">← {html.escape(prev["title"])}</a>' if prev else '<span></span>') \
        + (f'<a href="{nxt["slug"]}.html">{html.escape(nxt["title"])} →</a>' if nxt else '') + '</nav>'
    body = f'''<article class="project wrap narrow">
<a class="back" href="../index.html#work">← All work</a>
<p class="eyebrow">{html.escape(p.get("years", ""))}</p>
<h1>{html.escape(p["title"])}</h1>
<p class="lede">{html.escape(p.get("summary", ""))}</p>
{chips(p["tags"])}
{links_html(p.get("links"))}
</article>
<div class="wrap">{hero}</div>
<article class="project wrap narrow prose">
{md(blocks(slug, p["body"], pre))}
{pager}
</article>'''
    og = media(slug, p['hero']) if p.get('hero') else ''
    return page(f'{p["title"]} · Ben Vrakas', body, pre, p.get('summary', ''), og)


def card(p):
    slug = p['slug']
    img = (f'<img src="{media(slug, p["hero"], True)}" alt="" loading="lazy">' if p.get('hero')
           else f'<div class="codeart"><span>{html.escape(p.get("codeart", "</>"))}</span></div>')
    return f'''<a class="card" href="projects/{slug}.html">
<div class="thumb">{img}</div>
<div class="cbody"><p class="eyebrow">{html.escape(p.get("years", ""))}</p><h3>{html.escape(p["title"])}</h3>
<p>{html.escape(p.get("summary", ""))}</p>{chips(p["tags"][:4])}</div></a>'''


def build_home(projects):
    meta, body = front_matter(open(os.path.join(CONTENT, 'home.md'), encoding='utf-8').read())
    sections = re.split(r'^<!--\s*section:\s*(\w+)\s*-->\s*$', body, flags=re.M)
    sec = {sections[i]: sections[i + 1] for i in range(1, len(sections), 2)}
    grid = '<div class="grid">' + ''.join(card(p) for p in projects) + '</div>'
    hero_img = meta.get('hero_image', '')
    out = f'''<section class="hero wrap">
<div class="htext">
<p class="eyebrow">{html.escape(meta.get("eyebrow", ""))}</p>
<h1>{meta.get("tagline", "")}</h1>
<p class="lede">{html.escape(meta.get("intro", ""))}</p>
{chips([t.strip() for t in meta.get("skills", "").split(",") if t.strip()])}
</div>
{f'<div class="himg"><img src="{hero_img}" alt=""></div>' if hero_img else ''}
</section>
<section id="work" class="wrap"><h2 class="sh">Selected work</h2>{grid}</section>
<section id="experience" class="wrap narrow prose"><h2 class="sh">Experience</h2>{md(sec.get("experience", ""))}</section>
<section id="about" class="wrap narrow prose"><h2 class="sh">About</h2>{md(sec.get("about", ""))}</section>
<section id="contact" class="wrap narrow prose"><h2 class="sh">Elsewhere</h2>{md(sec.get("contact", ""))}</section>'''
    return page('Ben Vrakas · Mechanical design, electronics & software', out, '', meta.get('intro', ''),
                hero_img)


def main():
    projects = load_projects()
    os.makedirs(os.path.join(OUT, 'projects'), exist_ok=True)
    for i, p in enumerate(projects):
        prev = projects[i - 1] if i > 0 else None
        nxt = projects[i + 1] if i + 1 < len(projects) else None
        open(os.path.join(OUT, 'projects', p['slug'] + '.html'), 'w', encoding='utf-8').write(build_project(p, prev, nxt))
        for m in re.findall(r'^(?!:::)\s*([a-z0-9-]+)\s*\|', p['body'], re.M) + ([p['hero']] if p.get('hero') else []):
            if not os.path.exists(os.path.join(OUT, media(p['slug'], m))):
                print(f'  missing media: {p["slug"]}/{m}')
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(build_home(projects))
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print(f'built {len(projects)} projects -> docs/')


if __name__ == '__main__':
    main()
