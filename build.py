"""Build the Proteus static site. Run with python3 build.py. No dependencies."""
import json
from hashlib import sha256
from html import escape as esc
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape
from home_v2 import render_home
from icons import icon

ROOT = Path(__file__).parent
OUT = ROOT / 'dist'
DATA = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
ORIGIN = 'https://ahawkins4824-blip.github.io/proteus-sports-group'
# Enquiry form delivery. Paste the Web3Forms access key for info@proteus.nz here to make the
# contact form send messages directly. While it is empty the form prepares an email draft instead.
FORM_ACCESS_KEY = ''
MANIFEST_PATH = OUT / 'assets' / 'image-manifest.json'
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding='utf-8')) if MANIFEST_PATH.exists() else {}
SIZES = {'half':'(max-width:900px) 100vw, 50vw', 'full':'100vw', 'card':'(max-width:600px) 50vw, 33vw', 'small':'(max-width:600px) 50vw, 25vw', 'rail':'(max-width:600px) 80vw, 25vw'}
PUBLIC_ROUTES = []
ARROW = f'<span class="icon-wrap" aria-hidden="true">{icon("arrow-up-right")}</span>'
CHECK = f'<span class="tick" aria-hidden="true">{icon("check")}</span>'
PROGRAMMES = DATA['programmes']
BY_SLUG = {p['slug']: p for p in PROGRAMMES}
ALTS = {'early-years':'A young child enjoying a football kick on the grass', 'school':'A school football team and coaches together on the pitch', 'development':'Young football players and their coaches beside a goal', 'holiday':'Children and coaches together at a Proteus school sports programme', 'team':'The Proteus coaching team together beside their branded vehicle', 'community':'Children choosing sports equipment for an activity', 'academy-2027':'Proteus Academy 2027 expressions of interest for football and basketball', **DATA['images']}
AUDIENCES = [('players','For players'), ('schools','For schools & preschools'), ('community','For communities'), ('coaches','For coaches')]

def img(name, alt, cls='', eager=False, sizes='half'):
    """A photo with width/height (no layout jump) and smaller copies for small screens. Run optimise_images.py after adding photos."""
    info = MANIFEST.get(name, {})
    attrs = f'src="/assets/{name}.webp" alt="{esc(alt,quote=True)}"'
    if info:
        attrs += f' width="{info["width"]}" height="{info["height"]}"'
        if info['variants']:
            srcset = ', '.join([f'/assets/{name}-{w}.webp {w}w' for w in info['variants']] + [f'/assets/{name}.webp {info["width"]}w'])
            attrs += f' srcset="{srcset}" sizes="{SIZES.get(sizes, sizes)}"'
    return f'<img class="{cls}" {attrs} loading="{"eager" if eager else "lazy"}" decoding="async"'+(' fetchpriority="high"' if eager else '')+'>'

def image(name, cls='', eager=False, sizes='half'):
    return img(name, ALTS[name], cls, eager, sizes)

def visual(p, eager=False, rail=False, sizes='half'):
    """A programme's photo, or a branded graphic panel where no photo exists yet."""
    name = p.get('rail_image') if rail and p.get('rail_image') else p.get('image')
    if name:
        return image(name, eager=eager, sizes='rail' if rail else sizes)
    words = ''.join(f'<span>{esc(w)}</span>' for w in p['graphic'])
    return f'<div class="graphic-panel" role="img" aria-label="{esc(p["title"],quote=True)}: {esc(" ".join(p["graphic"]).lower(),quote=True)}"><div class="graphic-rings" aria-hidden="true"></div>{words}</div>'

def button(text, href, cls='button-primary'):
    return f'<a class="button {cls}" href="{esc(href, quote=True)}">{text}{ARROW}</a>'

def header(active=''):
    links = [('Programmes','/programmes/'), ('2026 update','/2026/'), ('Our approach','/about/'), ('Our people','/about/#team'), ('Contact','/contact/')]
    nav = ''.join(f'<a href="{url}"'+(' aria-current="page"' if name==active else '')+f'>{name}</a>' for name,url in links)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
    <div class="announcement"><span class="status-dot"></span> THE NEXT CHAPTER STARTS HERE <a href="/academy/">2027 Athlete Academy expressions of interest {ARROW}</a></div>
    <header class="site-header"><div class="header-inner"><a class="brand" href="/" aria-label="Proteus Sports Group home"><img src="/assets/logo.png" alt="Proteus Sports Group" width="225" height="68"></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav>{button('Find your programme','/programmes/','button-small')}<button id="menu-toggle" class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span></button></div><nav id="mobile-menu" class="mobile-menu" aria-label="Mobile navigation" hidden>{nav}<a href="/academy/">2027 Athlete Academy {ARROW}</a></nav></header>'''

def footer():
    links = ''.join(f'<a href="/{p["slug"]}/">{esc(p["title"])}</a>' for p in PROGRAMMES)
    return f'''<footer class="site-footer"><div class="container footer-top"><a href="/" class="brand footer-brand" aria-label="Proteus Sports Group home"><img src="/assets/logo.png" alt="Proteus Sports Group" width="225" height="68"></a><p>People first.<br>Development always.</p><div><span class="footer-label">START A CONVERSATION</span><a class="footer-email" href="mailto:info@proteus.nz">info@proteus.nz {ARROW}</a><span>Christchurch, New Zealand · Since 2018</span></div></div><nav class="container footer-programmes" aria-label="Programmes"><span class="footer-label">OUR PROGRAMMES</span><div>{links}</div></nav><div class="container footer-partner"><span class="footer-label">OUR APPAREL PARTNER</span><a href="https://www.dynastysport.co.nz/" target="_blank" rel="noopener noreferrer" aria-label="Dynasty Sport, our apparel partner (opens in a new tab)"><img src="/assets/dynasty-logo.webp" alt="Dynasty Sport" width="110" height="60" loading="lazy" decoding="async"></a></div><div class="container footer-bottom"><span>© 2026 Proteus Sports Group</span><nav aria-label="Footer navigation"><a href="/programmes/">Programmes</a><a href="/2026/">2026 update</a><a href="/contact/">Contact</a><a href="https://www.instagram.com/proteussportsgroup/" target="_blank" rel="noopener noreferrer">Instagram {ARROW}</a><a href="https://nz.linkedin.com/company/proteus-sports-group" target="_blank" rel="noopener noreferrer">LinkedIn {ARROW}</a><a href="/privacy-and-cookie-policy/">Privacy</a></nav></div></footer>'''

def asset_url(name):
    return '/'+name+'?v='+sha256((OUT/name).read_bytes()).hexdigest()[:12]

def short_desc(desc, limit=158):
    if len(desc) <= limit:
        return desc
    cut = desc[:limit]
    end = max(cut.rfind('. '), cut.rfind(': '))
    return cut[:end+1] if end > 80 else cut[:cut.rfind(' ')].rstrip(',;:') + '…'

ORG_JSONLD = json.dumps({
    '@context': 'https://schema.org', '@type': 'SportsOrganization', 'name': 'Proteus Sports Group',
    'url': ORIGIN + '/', 'logo': ORIGIN + '/assets/logo.png', 'image': ORIGIN + '/assets/team.jpg',
    'email': 'info@proteus.nz', 'foundingDate': '2018', 'slogan': DATA['tagline'],
    'description': 'Sports coaching for players, preschools, schools, clubs, communities and retirement villages across Christchurch and Canterbury.',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Christchurch', 'addressRegion': 'Canterbury', 'addressCountry': 'NZ'},
    'areaServed': {'@type': 'AdministrativeArea', 'name': 'Canterbury, New Zealand'},
    'sport': DATA['sports'],
    'sameAs': ['https://www.instagram.com/proteussportsgroup/', 'https://nz.linkedin.com/company/proteus-sports-group'],
}, ensure_ascii=False).replace('</', '<\\/')

def layout(title, desc, body, active='', route='/', indexable=True):
    robots = 'index,follow' if indexable else 'noindex,follow'
    desc = short_desc(desc)
    return f'''<!doctype html><html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Proteus Sports Group</title><meta name="description" content="{esc(desc,quote=True)}"><meta name="theme-color" content="#35175c"><meta name="robots" content="{robots}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="canonical" href="{ORIGIN}{route}"><meta property="og:title" content="{esc(title,quote=True)} | Proteus Sports Group"><meta property="og:description" content="{esc(desc,quote=True)}"><meta property="og:type" content="website"><meta property="og:image" content="{ORIGIN}/assets/team.jpg"><meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">{ORG_JSONLD}</script><link rel="preload" href="/assets/fonts/headline.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{asset_url('styles.css')}"><link rel="stylesheet" href="{asset_url('motion.css')}"><link rel="stylesheet" href="{asset_url('scale.css')}"><script src="{asset_url('app.js')}" defer></script><script src="{asset_url('motion.js')}" defer></script></head><body class="{'home-immersive' if route=='/' else ''}">{header(active)}<main id="main">{body}</main>{footer()}</body></html>'''

def faq(limit=None, items=None):
    items = items if items is not None else DATA['faq'][:limit]
    return '<div class="faq-list">'+''.join(f'<details><summary>{esc(x["question"])}<span class="faq-icon" aria-hidden="true">{icon("plus")}</span></summary><p>{esc(x["answer"])}</p></details>' for x in items)+'</div>'

# Shared "scale" sections used on the homepage, About and 2026 pages.
def stats_band(eyebrow='PROTEUS BY THE NUMBERS · 2026', title='ONE TEAM.<br><span>EVERY LEVEL.</span>', text='From first kicks at age two to Active Age in retirement villages, our coaches are out across Christchurch every day of the week: in preschools, schools, clubs, holiday camps and community spaces.'):
    stats = ''.join(f'<li class="reveal"><strong>{esc(s["value"])}</strong><span class="stat-label">{esc(s["label"])}</span><span class="stat-note">{esc(s["note"])}</span></li>' for s in DATA['stats'])
    sports = ''.join(f'<li{" class=core" if i==0 else ""}>{esc(s)}{" <em>Core sport</em>" if i==0 else ""}</li>' for i,s in enumerate(DATA['sports']))
    return f'<section class="scale-band" aria-labelledby="scale-heading"><div class="container"><div class="scale-head reveal"><div><p class="eyebrow">{eyebrow}</p><h2 id="scale-heading">{title}</h2></div><p>{text}</p></div><ul class="scale-stats">{stats}</ul><div class="scale-sports reveal"><span class="eyebrow">SPORTS WE COACH</span><ul>{sports}</ul></div></div></section>'

PARTNER_GROUPS = [('schools','Schools & colleges'), ('clubs','Clubs'), ('community','Community partners')]

def partner_list(key):
    return '<ul>'+''.join(f'<li>{esc(n)}</li>' for n in DATA['partners'][key])+'</ul>'

def testimonials(section_id='testimonials', heading=True):
    cards = ''.join(f'<figure class="testimonial reveal"><blockquote><p>“{esc(q["quote"])}”</p></blockquote><figcaption><strong>{esc(q["name"])}</strong><span>{esc(q["role"])}'+(f', {esc(q["org"])}' if q.get('org') else '')+'</span></figcaption></figure>' for q in DATA['testimonials'])
    head = '<div class="section-heading"><div><p class="eyebrow">IN THEIR WORDS</p><h2>WHAT OUR<br><span class="text-purple">PARTNERS SAY.</span></h2></div><p>Feedback from schools and clubs we coach with.</p></div>' if heading else ''
    return f'<div class="testimonials" id="{section_id}">{head}<div class="testimonial-grid">{cards}</div></div>'

def trust_section():
    """Homepage summary of who we work with; the full partner lists live on the About page."""
    return f'<section class="partners-wall trust-section" aria-labelledby="trust-heading"><div class="container"><div class="partners-head reveal"><div><p class="eyebrow">TRUSTED ACROSS CANTERBURY</p><h2 id="trust-heading">SCHOOLS. CLUBS.<br><span>COMMUNITIES.</span></h2></div><p>From grassroots clubs and early learning centres to some of New Zealand’s leading schools.</p></div>{reach_strip()}{testimonials("testimonials", heading=False)}<div class="trust-more">{button("See who we work with","/about/#partners","button-secondary")}</div></div></section>'

def partners_wall(section_id='partners'):
    cols = ''.join(f'<div class="partners-col reveal"><h3><span>{len(DATA["partners"][k]):02d}</span>{label}</h3>{partner_list(k)}</div>' for k,label in PARTNER_GROUPS)
    return f'<section class="partners-wall" id="{section_id}" aria-labelledby="{section_id}-heading"><div class="container"><div class="partners-head reveal"><div><p class="eyebrow">TRUSTED ACROSS CANTERBURY</p><h2 id="{section_id}-heading">SCHOOLS. CLUBS.<br><span>COMMUNITIES.</span></h2></div><p>From grassroots clubs and early learning centres to some of New Zealand’s leading schools. Here are some of the organisations we’re proud to partner with.</p></div>{reach_strip()}<div class="partners-cols">{cols}</div></div></section>'

def pathway(full=False):
    stages = []
    for i, st in enumerate(DATA['pathway'], 1):
        links = ''.join(f'<a href="/{slug}/">{esc(BY_SLUG[slug]["title"])} {ARROW}</a>' for slug in st['links'])
        body = '<ul>'+''.join(f'<li>{esc(x)}</li>' for x in st['items'])+'</ul>' if full else f'<p>{esc(st["summary"])}</p>'
        stages.append(f'<li class="pathway-stage reveal"><span class="pathway-num">{i:02d}</span><h3>{esc(st["title"])}</h3>{body}<div class="pathway-links">{links}</div></li>')
    return f'<section class="pathway-section{" pathway-full" if full else ""}" aria-labelledby="pathway-heading"><div class="container"><div class="pathway-head reveal"><div><p class="eyebrow">THE PROTEUS COACHING & DEVELOPMENT PIPELINE</p><h2 id="pathway-heading">ONE CONNECTED<br><span>PATHWAY.</span></h2></div><p>From early sporting fundamentals to advanced coaching, performance environments and industry development, Proteus supports participants, coaches and organisations at every stage of the sporting journey.</p></div><ol class="pathway-track">{"".join(stages)}</ol><p class="pathway-tagline"><strong>{esc(DATA["tagline"])}</strong> We combine people, systems, partnerships and industry knowledge to deliver programmes that are accessible, sustainable and impactful.</p></div></section>'

def reach_strip():
    items = ''.join(f'<li><strong>{esc(r["value"])}</strong><span>{esc(r["text"])}</span></li>' for r in DATA['reach'])
    return f'<div class="reach-strip reveal"><p class="eyebrow">SINCE 2018, WE’VE WORKED WITH</p><ul>{items}</ul></div>'

def card_audience(p):
    return ' '.join(p['tags'])

def cards():
    result=[]
    for n,p in enumerate(PROGRAMMES,1):
        slug=p['slug']; academy = slug=='academy'
        result.append(f'''<article class="programme-card {'academy-card' if academy else ''}" data-programme-card data-audience="{card_audience(p)}"><a href="/{slug}/" class="card-link"><div class="card-image">{visual(p, sizes="card")}<span class="card-number">{n:02d}</span><span class="card-arrow" aria-hidden="true">{icon("arrow-up-right")}</span>{'<span class="card-tag">2027 INTAKE</span>' if academy else ''}</div><div class="card-body"><p class="card-label">{esc(p["label"])}</p><h3>{esc(p["title"])}</h3><p>{esc(p["caption"])}</p></div></a></article>''')
    return ''.join(result)

def cta(title='Your next chapter<br>starts with a conversation.',text='A player with a goal? A school with a plan? Let’s make it happen together.'):
    return f'<section class="cta-section"><div class="container cta-inner"><div><p class="eyebrow">LET’S GET STARTED</p><h2>{title}</h2><p>{text}</p></div>{button("Talk to our team", "/contact/", "button-lime")}</div></section>'

def programmes():
    filters = '<button data-filter="all" aria-pressed="true">All programmes</button>'+''.join(f'<button data-filter="{k}" aria-pressed="false">{label}</button>' for k,label in AUDIENCES)
    return f'''<section class="page-intro"><div class="container"><p class="eyebrow">OUR PROGRAMMES</p><h1>FIND YOUR<br><span>NEXT STEP.</span></h1><p>Nine programmes, nearly 60 coaches and one team. From first kicks at age two to performance coaching, school sport, community events and Active Age in retirement villages.</p></div></section><section class="section programme-section"><div class="container"><div class="filter-bar"><div class="programme-filters" data-programme-filters role="group" aria-label="Filter programmes">{filters}</div><span id="programme-count" aria-live="polite">{len(PROGRAMMES)} programmes</span></div><div class="programme-grid">{cards()}</div><p id="programmes-empty" hidden>No programmes match this filter. Our team can help you find an option.</p></div></section>{pathway()}{cta('NOT SURE WHERE<br>TO START?', 'Tell us a little about your goals. We’ll help you find the right fit.')}'''

def detail_extras(p):
    out = ''
    if p.get('facts'):
        facts = ''.join(f'<li><strong>{esc(v)}</strong><span>{esc(l)}</span></li>' for v,l in p['facts'])
        out += f'<section class="detail-facts" aria-label="{esc(p["title"],quote=True)} at a glance"><div class="container"><ul>{facts}</ul></div></section>'
    blocks = ''
    if p.get('list'):
        items = ''.join(f'<li>{CHECK}{esc(i)}</li>' for i in p['list']['items'])
        blocks += f'<div class="detail-block"><p class="eyebrow">{esc(p["list"]["title"])}</p><ul class="tick-list">{items}</ul></div>'
    if p.get('partners'):
        label = dict(PARTNER_GROUPS)[p['partners']]
        blocks += f'<div class="detail-block detail-partners"><p class="eyebrow">{label} we’ve partnered with</p>{partner_list(p["partners"])}</div>'
    if p.get('story'):
        s = p['story']
        blocks += f'<figure class="detail-block detail-story"><p class="eyebrow">{esc(s["title"])}</p><blockquote>“{esc(s["quote"])}”</blockquote><figcaption>{esc(s["text"])}</figcaption></figure>'
    if blocks:
        out += f'<section class="section detail-blocks-section"><div class="container detail-blocks">{blocks}</div></section>'
    if p.get('gallery'):
        out += '<section class="detail-gallery" aria-label="Photos from the programme"><div class="container"><div class="gallery-grid">'+''.join(f'<figure>{image(g, sizes="card")}</figure>' for g in p['gallery'])+'</div></div></section>'
    return out

def camp_details(p):
    c = p.get('camps')
    if not c:
        return ''
    r = c['recent']
    if c.get('upcoming'):
        rows = ''.join(f'<li><strong>{esc(u["name"])}</strong><span>{esc(u["dates"])} · {esc(u["location"])}</span><span>{esc(u["cost"])}</span></li>' for u in c['upcoming'])
        upcoming = f'<ul class="camp-list">{rows}</ul>'
    else:
        upcoming = '<p>Dates and locations for the next school holidays will be posted here once they’re confirmed. Register your interest and we’ll email you the details.</p>'
    guide = ''.join(f'<div><dt>{k}</dt><dd>{esc(v)}</dd></div>' for k,v in [('Cost', r['cost']+'. '+r['discount']+'.'), ('Typical day', r['time']), ('Ages', r['ages']), ('Last camp', r['dates']+', '+r['location'])])
    return f'''<section class="section camp-section" id="dates" aria-labelledby="camp-heading"><div class="container camp-grid"><div class="camp-upcoming"><p class="eyebrow">DATES & PRICES</p><h2 id="camp-heading">UPCOMING<br><span class="text-purple">PROGRAMMES.</span></h2>{upcoming}{button('Register your interest','/contact/?programme='+quote(p['title']),'button-primary')}</div><div class="camp-guide"><p class="eyebrow">WHAT TO EXPECT</p><h3>{esc(r['name'])}</h3><p class="camp-partner">{esc(r['partner'])}. Our most recent performance camp is a good guide to price and format.</p><dl>{guide}</dl><p class="camp-sponsor">Holiday camps proudly sponsored by <a href="https://www.dynastysport.co.nz/" target="_blank" rel="noopener noreferrer">Dynasty Sport</a>.</p></div></div></section>'''

def programme_faq(p):
    items = list(p.get('faq', [])) + [DATA['faq'][i] for i in p.get('faqGeneral', [0])]
    return faq(items=items)

def programme(p):
    slug=p['slug']; is_academy=slug=='academy'
    features=''.join(f'<article><span>0{i}</span><h3>{esc(f["title"])}</h3><p>{esc(f["text"])}</p></article>' for i,f in enumerate(p['features'],1))
    if is_academy:
        sports=' · '.join(esc(c['label']) for c in p['contacts'])
        contacts=f'<div class="academy-contacts"><a href="/contact/?programme={quote(p["title"])}"><span>{sports}</span><h3>Express your interest {ARROW}</h3><p>info@proteus.nz</p></a></div>'
        extra=f'<section class="section"><div class="container"><p class="eyebrow">TAKE THE FIRST STEP</p><h2>YOUR JOURNEY.<br><span class="text-purple">LET’S TALK.</span></h2><p class="measure">{esc(p["enquiryGuidance"])}</p>{contacts}</div></section>'
    else: extra=''
    index = PROGRAMMES.index(p)
    next_band = '' if is_academy else f'''<section class="detail-next"><div class="container"><div><p class="eyebrow">LET’S MAKE A PLAN</p><h2>{esc(p['cta'])}.</h2><p>Talk to our team about options, availability and the next steps.</p></div>{button('Start a conversation','/contact/?programme='+quote(p['title']),'button-primary')}</div></section>'''
    nxt = PROGRAMMES[(index+1) % len(PROGRAMMES)]
    return f'''<section class="detail-hero"><div class="detail-copy"><a class="back-link" href="/programmes/">{icon("arrow-left")} All programmes</a><p class="eyebrow">{index+1:02d} / {len(PROGRAMMES):02d} · {esc(p['eyebrow'])}</p><h1>{esc(p['title'])}</h1><p>{esc(p['intro'])}</p>{button(esc(p['cta']),'/contact/?programme='+quote(p['title']),'button-lime')}</div><div class="detail-photo">{visual(p, eager=True)}<span class="image-caption">THE PROTEUS WAY / {'2027 ACADEMY' if is_academy else esc(p['label'])}</span></div></section><section class="section"><div class="container"><div class="detail-intro"><p class="eyebrow">WHO IT’S FOR</p><h2>{esc(p['audience'])}</h2></div><div class="detail-features">{features}</div></div></section>{camp_details(p)}{detail_extras(p)}{extra}{next_band}<nav class="next-programme" aria-label="Next programme"><div class="container"><a href="/{nxt['slug']}/"><span class="eyebrow">NEXT PROGRAMME · {(index+2) if index+1 < len(PROGRAMMES) else 1:02d}</span><strong>{esc(nxt['title'])}</strong>{ARROW}</a></div></nav><section class="section faq-section"><div class="container faq-grid"><div><p class="eyebrow">HERE TO HELP</p><h2>GOOD<br><span class="text-purple">QUESTIONS.</span></h2><a class="text-link" href="/contact/?programme={quote(p['title'])}">Ask us something else {ARROW}</a></div>{programme_faq(p)}</div></section>'''

def beyond_coaching():
    cards = ''.join(f'<article><span>0{i}</span><h3>{esc(b["title"])}</h3><p>{esc(b["text"])}</p></article>' for i,b in enumerate(DATA['beyond'],1))
    return f'<section class="section beyond-section"><div class="container"><div class="section-heading"><div><p class="eyebrow">MORE THAN COACHING</p><h2>PEOPLE. SYSTEMS.<br><span class="text-purple">PARTNERSHIPS.</span></h2></div><p>Helping partners build sustainable programmes with impact beyond the session.</p></div><div class="detail-features">{cards}</div></div></section>'

def football_core():
    items = ''.join(f'<li>{CHECK}{esc(x)}</li>' for x in DATA['philosophy'])
    return f'''<section class="football-core"><div class="container football-core-grid"><div><p class="eyebrow">OUR SPECIALITY</p><h2>FOOTBALL<br><span>AT OUR CORE.</span></h2><p>We work across many sports and communities, but our coaching foundations are rooted in football. With more than 10 years in the industry, our expertise spans grassroots and amateur football through to semi-professional and high-performance settings.</p><p>Our football operations are led by our Director, an OFC A Licence coach who also oversees the academy and first-team environments at a large membership-based club. We have a track record of helping players progress well beyond the environments where they started.</p><div class="football-core-facts"><span><strong>10+</strong>Years in football</span><span><strong>OFC A</strong>Licence-qualified Director</span></div></div><div class="football-core-list"><p class="eyebrow">OUR COACHING PHILOSOPHY</p><p>Football is the foundation of our methodology. Its principles shape how we coach every sport, with emphasis on:</p><ul class="tick-list">{items}</ul></div></div></section>'''

def about():
    team=''.join(f'<article class="team-person">'+(image(p['photo'],'person-photo',sizes='small') if p.get('photo') else f'<span class="person-initials" aria-hidden="true">{"".join(n[0] for n in p["name"].split())}</span>')+f'<p class="eyebrow">{esc(p["role"])}</p><h3>{esc(p["name"])}</h3><p>{esc(p["text"])}</p>'+ (f'<a class="text-link" href="mailto:{p["email"]}">Say hello {ARROW}</a>' if p.get('email') else '') + '</article>' for p in DATA['team'])
    return f'''<section class="page-intro"><div class="container"><p class="eyebrow">WE’RE PROTEUS SPORTS GROUP</p><h1>SPORT BRINGS<br><span>US TOGETHER.</span></h1><p>Established in 2018 to provide accessible coaching to any player, organisation or sporting environment, regardless of level or ability. Today nearly 60 coaches deliver across Canterbury, and people are at the heart of everything we do.</p></div></section><div class="about-banner">{image('pa-camp-squad',eager=True,sizes='full')}<span>QUALITY COACHING. STRONGER COMMUNITIES.</span></div><section class="section"><div class="container intro-grid"><p class="eyebrow">OUR STORY</p><div><h2>BUILT FOR<br><span class="text-purple">TRANSFORMATION.</span></h2><div class="two-col-copy"><p>Proteus Sports Group was founded in 2018 by Oliver Hawkins and Myles Gardner. Proteus was the Greek god who could change his form, and transformation is what we’re about: shaping players, building skills and helping people become better team-mates. We take pride in creating employment and coaching opportunities in the local sports industry, strengthening the wider sporting ecosystem.</p><p>Since 2019 we’ve built long-term partnerships with colleges, clubs and organisations throughout Canterbury. Through them we recruit, support and manage coaching programmes, establish new initiatives and help sporting structures grow. Our network means we deliver more than coaching, with the operational support and sports business capability to create impact well beyond the session.</p></div></div></div></section>{pathway(full=True)}{beyond_coaching()}{football_core()}<section class="section about-values"><div class="container"><p class="eyebrow">THE PROTEUS WAY</p><div class="principles"><article><span>01 / SIMPLICITY</span><h3>Make it easy.</h3><p>Clear communication and end-to-end coaching support, built around what your people need.</p></article><article><span>02 / QUALITY</span><h3>Make it count.</h3><p>Professional coaches who bring purpose, energy and care to their sessions.</p></article><article><span>03 / COMMUNITY</span><h3>Make it for everyone.</h3><p>Welcoming sporting environments that encourage connection and participation.</p></article></div></div></section><section class="section" id="team"><div class="container"><div class="section-heading"><div><p class="eyebrow">OUR PEOPLE</p><h2>THE PEOPLE<br><span class="text-purple">IN YOUR CORNER.</span></h2></div><p>An internal management team backed by nearly 60 coaches.<br>People first. Development always.</p></div><div class="team-grid" id="team-link">{team}</div><div class="join-team"><div><p class="eyebrow">BRING YOUR ENERGY</p><h3>Your next step could be coaching.</h3><p>Join a network of nearly 60 coaches across schools, clubs, early learning centres and community sport, with quick onboarding, reliable fortnightly payments and real support to grow. We’re registering interest for 2027 now.</p></div>{button('Explore coaching opportunities','/contact/?interest=Coaching%20opportunities','button-secondary')}</div></div></section>{partners_wall()}{cta()}'''

def update_2026():
    u = DATA['update2026']
    record = ''.join(f'<li>{CHECK}{esc(x)}</li>' for x in u['record'])
    sections = ''.join(f'<article class="update-story reveal"><div class="update-story-photo">{image(s["image"], sizes="small")}</div><div><p class="eyebrow">{esc(s["label"])}</p><h3>{esc(s["title"])}</h3><p>{esc(s["text"])}</p></div></article>' for s in u['sections'])
    leaders = ''.join(f'<article class="team-person">'+(image(l['photo'],'person-photo',sizes='small') if l.get('photo') else f'<span class="person-initials" aria-hidden="true">{"".join(n[0] for n in l["name"].split())}</span>')+f'<p class="eyebrow">{esc(l["role"])}</p><h3>{esc(l["name"])}</h3><p>{esc(l["text"])}</p></article>' for l in u['leadership'])
    coaches = ''.join(f'<li>{esc(c)}</li>' for c in u['coaches'])
    ahead = ''.join(f'<li><span>{i:02d}</span>{esc(a)}</li>' for i,a in enumerate(u['ahead'],1))
    sports = ''.join(f'<li{" class=core" if i==0 else ""}>{esc(s)}{" <em>Primary focus</em>" if i==0 else ""}</li>' for i,s in enumerate(DATA['sports']))
    return f'''<section class="update-hero"><div class="update-hero-photo">{image('pa-club-squad',eager=True,sizes='full')}</div><div class="container update-hero-copy"><p class="eyebrow"><span class="status-dot"></span> 2026 UPDATE · QUARTER ONE</p><h1>A RECORD<br><span>START.</span></h1><p>{esc(u['intro'])}</p></div></section><section class="update-record"><div class="container update-record-grid"><div><p class="eyebrow">ACROSS TERM ONE, WE</p><h2>A RECORD<br><span class="text-purple">QUARTER.</span></h2></div><ul class="tick-list tick-list-large">{record}</ul></div></section>{stats_band('2026 IN NUMBERS','THE MOMENTUM<br><span>IS BUILDING.</span>','This level of delivery reflects both the demand for quality coaching and the strength of the Proteus network.')}<section class="section"><div class="container"><div class="section-heading"><div><p class="eyebrow">WHAT’S BEEN HAPPENING</p><h2>EVERY CORNER<br><span class="text-purple">OF THE GAME.</span></h2></div><p>Schools, clubs, holidays,<br>individuals and early years.</p></div><div class="update-stories">{sections}</div></div></section><section class="update-sports"><div class="container update-sports-grid"><div><p class="eyebrow">EXPANDING INTO NEW SPORTS</p><h2>FOOTBALL FIRST.<br><span>AND MORE.</span></h2><p>Football remains the heart of Proteus. Growing demand from schools and clubs has taken us into five more codes, with recruitment pathways led by Isaac Rockell.</p></div><ul class="sport-tiles">{sports}</ul></div></section><section class="section"><div class="container"><div class="section-heading"><div><p class="eyebrow">STRENGTHENING OUR LEADERSHIP</p><h2>QUALITY<br><span class="text-purple">AT SCALE.</span></h2></div><p>New roles to support<br>a growing coaching workforce.</p></div><div class="team-grid team-grid-3">{leaders}</div></div></section><section class="coach-roll"><div class="container"><div class="coach-roll-head"><div><p class="eyebrow">THE BACKBONE OF PROTEUS</p><h2>OUR TERM ONE<br><span>COACHING TEAM.</span></h2></div><p>Returning faces and new additions. Their professionalism, enthusiasm and commitment to athlete development make everything we do possible.</p></div><ul class="coach-names">{coaches}</ul></div></section><section class="section"><div class="container update-ahead"><div><p class="eyebrow">LOOKING AHEAD</p><h2>INTO THE<br><span class="text-purple">BUSY SEASON.</span></h2><p class="update-signoff">“2026 is off to an outstanding start, and we are excited for what lies ahead.”<span>Oliver Hawkins, Director</span></p></div><ol class="ahead-list">{ahead}</ol></div></section>{cta('BE PART OF<br>WHAT’S NEXT.','A programme for your school, club, centre or community? A place in our coaching team? Let’s talk.')}'''

def contact():
    sends = bool(FORM_ACCESS_KEY)
    form_lead = 'Send us a message and our team will get back to you by email.' if sends else 'Prepare a message below, then open it in your email app to send to our team.'
    form_button = 'Send enquiry' if sends else 'Prepare enquiry'
    form_note = 'We only use your details to reply to your enquiry.' if sends else 'Your message is only sent when you send the email from your email app.'
    form_key = f' data-access-key="{esc(FORM_ACCESS_KEY, quote=True)}"' if sends else ''
    interests=['General enquiry']+[p['title'] for p in PROGRAMMES]+['Academy — '+c['label'].lower() for c in BY_SLUG['academy']['contacts']]+['Club coaching','Sponsorship & partnerships','Coaching opportunities']
    opts=''.join(f'<option value="{esc(x,quote=True)}">{esc(x)}</option>' for x in interests)
    return f'''<section class="page-intro contact-intro"><div class="container"><p class="eyebrow">GET IN TOUCH</p><h1>LET’S MAKE<br><span>IT HAPPEN.</span></h1><p>Tell us what you have in mind. We’ll help you find the right programme, people and next step.</p></div></section><section class="section contact-section"><div class="container contact-grid"><aside class="contact-details"><p class="eyebrow">A CONVERSATION IS A GOOD START</p><h2>YOUR GOALS.<br>OUR TEAM.</h2><a class="contact-email" href="mailto:info@proteus.nz">info@proteus.nz {ARROW}</a><p>Based in Christchurch, New Zealand.<br>Working with players, schools, clubs<br>and communities across Canterbury.</p><div class="contact-people"><a href="mailto:patrick@proteus.nz"><span>COACHING, SCHOOLS & TEACHER AID</span><strong>Patrick Rousse {ARROW}</strong><span>patrick@proteus.nz</span></a><a href="mailto:oliver@proteus.nz"><span>HOLIDAYS & SPONSORSHIP</span><strong>Oliver Hawkins {ARROW}</strong><span>oliver@proteus.nz</span></a><a href="mailto:isaac@proteus.nz"><span>BASKETBALL</span><strong>Isaac Rockell {ARROW}</strong><span>isaac@proteus.nz</span></a></div></aside><div class="enquiry-panel"><h3>Start your enquiry</h3><p>{form_lead}</p><noscript><p>Please email <a href="mailto:info@proteus.nz">info@proteus.nz</a>. The enquiry form needs JavaScript.</p></noscript><form id="enquiry-form" action="mailto:info@proteus.nz" method="post" enctype="text/plain"{form_key}><input class="form-trap" type="checkbox" name="botcheck" tabindex="-1" autocomplete="off" aria-hidden="true"><div class="form-row"><div class="field"><label for="enquiry-name">Your name <span>(required)</span></label><input id="enquiry-name" name="name" autocomplete="name" required maxlength="100" placeholder="First and last name"></div><div class="field"><label for="enquiry-address">Email address <span>(required)</span></label><input id="enquiry-address" name="email" type="email" autocomplete="email" required maxlength="200" placeholder="you@example.com"></div></div><div class="field"><label for="enquiry-interest">I’m interested in</label><select id="enquiry-interest" name="interest">{opts}</select></div><div class="field"><label for="enquiry-message">What do you have in mind? <span>(required)</span></label><textarea id="enquiry-message" name="message" rows="6" required maxlength="5000" placeholder="Tell us about your goals, sport, school, club or group…"></textarea></div><button class="button button-primary" type="submit" data-submit-label><span data-submit-text>{form_button}</span> {ARROW}</button><p class="form-note">{form_note}</p><p id="enquiry-status" class="form-status" role="status" aria-live="polite"></p></form><div id="enquiry-sent" class="enquiry-sent" hidden><p class="eyebrow">MESSAGE SENT</p><h3 tabindex="-1">Thanks. Your enquiry is on its way.</h3><p>Our team will reply to the email address you gave us. For anything urgent, email <a href="mailto:info@proteus.nz">info@proteus.nz</a>.</p></div><div id="enquiry-preview" class="enquiry-preview" hidden><p class="eyebrow">YOUR ENQUIRY IS READY TO REVIEW</p><h3>One more step: send your email.</h3><p id="enquiry-fallback-note" class="form-note" hidden>We couldn’t send your message automatically, so we’ve prepared it as an email instead.</p><label for="enquiry-summary">Your prepared message</label><textarea id="enquiry-summary" rows="9" readonly></textarea><div class="button-row"><a id="enquiry-email" class="button button-primary" href="mailto:info@proteus.nz">Open email draft {ARROW}</a><button id="copy-enquiry" class="button button-secondary" type="button">Copy message</button></div><p id="copy-status" role="status" aria-live="polite"></p></div><div class="contact-alternative"><p>Prefer to email us directly?</p><a class="text-link" href="mailto:info@proteus.nz">info@proteus.nz {ARROW}</a></div></div></div></section><section class="section faq-section"><div class="container faq-grid"><div><p class="eyebrow">BEFORE YOU GET IN TOUCH</p><h2>GOOD<br><span class="text-purple">QUESTIONS.</span></h2></div>{faq()}</div></section>'''

def write(route,title,desc,body,active=''):
    PUBLIC_ROUTES.append(route)
    folder=OUT / route.strip('/'); folder.mkdir(parents=True,exist_ok=True)
    (folder/'index.html').write_text(layout(title,desc,body,active,route), encoding='utf-8')

PARTS = {'visual': visual, 'stats_band': stats_band, 'trust': trust_section, 'img': img}
write('/','Sports coaching in Christchurch','Nearly 60 coaches, six sports and nine programmes. Sports coaching for players, preschools, schools, clubs and communities across Christchurch.',render_home(image,button,faq,cta,DATA,ARROW,PARTS))
write('/programmes/','Find your programme','Explore all nine Proteus programmes, from individual coaching and the 2027 Athlete Academy to school sport, holiday programmes and Active Age.',programmes(),'Programmes')
write('/2026/','2026 update','A record start to 2026 for Proteus Sports Group: nearly 60 coaches, six sports and hundreds of athletes supported every week across Christchurch.',update_2026(),'2026 update')
write('/about/','Our approach & people','Founded in 2018, Proteus Sports Group is Canterbury’s trusted coaching team. Meet our people and the schools, clubs and communities we work with.',about(),'Our approach')
write('/contact/','Get in touch','Talk to the Proteus Sports Group team about sports coaching, school programmes, the Academy and opportunities in Christchurch.',contact(),'Contact')
for p in PROGRAMMES:
    write('/'+p['slug']+'/',p['title'],p.get('meta') or p['intro'],programme(p),'Programmes')
(OUT/'404.html').write_text(layout('Page not found','Find your way back to Proteus Sports Group.',f'<section class="page-intro"><div class="container"><p class="eyebrow">404 / A LITTLE OFF THE PITCH</p><h1>LET’S GET YOU<br><span>BACK IN PLAY.</span></h1><p>We couldn’t find that page. Our programmes are a good place to start.</p>{button("Explore programmes","/programmes/","button-primary")}</div></section>', indexable=False), encoding='utf-8')
(OUT/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#35175c"/><text x="32" y="46" text-anchor="middle" font-family="Arial,sans-serif" font-size="44" font-weight="bold" fill="#d7ef70">P</text></svg>')
# Search engines may index current pages; saved designs stay out of search.
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /approved-v1/\nDisallow: /approved-v2/\nDisallow: /approved-v3/\n\nSitemap: '+ORIGIN+'/sitemap.xml\n')



# Carry the existing Proteus policy into the standalone site.
policy = (ROOT/'privacy_content.html').read_text(encoding='utf-8')
policy_intro = '<div class="policy-context"><p>This is the existing Proteus Sports Group privacy and cookies policy, covering our website and linked services. '+('Our enquiry form sends your message to our team by email through Web3Forms, a form delivery service; we only use your details to reply.' if FORM_ACCESS_KEY else 'Our enquiry form prepares an email draft on your device, which you send through your own email app.')+'</p></div>'
write('/privacy-and-cookie-policy/', 'Privacy and cookies policy', 'Proteus Sports Group privacy and cookies policy, including how to contact our team.', '<section class="section"><article class="container policy-article">'+policy_intro+policy+'</article></section>')

# Preserve the former Squarespace entry points while canonical pages use the new routes.
LEGACY_REDIRECTS = {
    '/home': '/',
    '/contact-1': '/contact/',
    '/preschool': '/early-years-fundamentals/',
    '/first-kicks': '/early-years-fundamentals/',
    '/little-play-kicks': '/early-years-fundamentals/',
    '/schools-sports': '/school-sports-coaching/',
    '/football-in-schools': '/school-sports-coaching/',
    '/primary-intermediate-schools': '/school-sports-coaching/',
    '/secondary-schools-colleges': '/school-sports-coaching/',
    '/football-11': '/individual-performance-coaching/',
    '/programmes-2': '/individual-performance-coaching/',
    '/active-age-programme-1': '/active-age-programme/',
    '/aca-coaches-union': '/coach-development/',
    '/who-we-work-with': '/about/#partners',
    '/who-we-work-with-1': '/about/#partners',
    '/clubs': '/about/#partners',
    '/coaching': '/contact/?interest=Coaching%20opportunities',
    '/positions': '/contact/?interest=Coaching%20opportunities',
    '/cookies-policy': '/privacy-and-cookie-policy/#cookies-policy',
    '/testimonials': '/#testimonials',
    '/sponsor': '/contact/?interest=Sponsorship%20%26%20partnerships',
}
redirect_rules = []
for old, target in LEGACY_REDIRECTS.items():
    folder = OUT/old.strip('/'); folder.mkdir(parents=True, exist_ok=True)
    destination = esc(target, quote=True)
    (folder/'index.html').write_text('<!doctype html><html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url='+destination+'"><link rel="canonical" href="'+esc(ORIGIN+target.split('#')[0],quote=True)+'"><title>Continue to Proteus Sports Group</title></head><body><p>This page has moved. <a href="'+destination+'">Continue to Proteus Sports Group</a>.</p></body></html>', encoding='utf-8')
    redirect_rules.extend([old+' '+target+' 301', old+'/ '+target+' 301'])
(OUT/'_redirects').write_text('\n'.join(redirect_rules)+'\n')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+xml_escape(ORIGIN+route)+'</loc></url>\n' for route in PUBLIC_ROUTES)+'</urlset>\n')
print(f'Built {len(PUBLIC_ROUTES)} canonical pages, {len(LEGACY_REDIRECTS)} legacy routes and saved snapshots.')
