"""Build the Proteus static site. Run with python3 build.py. No dependencies."""
import json
from hashlib import sha256
from html import escape as esc
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape
from home_v2 import render_home

ROOT = Path(__file__).parent
OUT = ROOT / 'dist'
DATA = json.loads((ROOT / 'content.json').read_text())
ORIGIN = 'https://ahawkins4824-blip.github.io/proteus-sports-group'
LEGACY_ORIGIN = 'https://proteus-sports.squarespace.com'
PUBLIC_ROUTES = []
ARROW = '<span aria-hidden="true">↗</span>'
IMAGES = {
 'individual-performance-coaching': 'development', 'academy': 'school',
 'early-years-fundamentals': 'early-years', 'school-sports-coaching': 'school',
 'holiday-programmes': 'holiday', 'coach-development': 'team'
}
SHORT = {
 'individual-performance-coaching': ('Individual & small group', 'A little extra focus. A whole new level.'),
 'academy': ('Proteus Academy', 'For ambitious football and basketball players. 2027 intake.'),
 'early-years-fundamentals': ('Early years & fundamentals', 'First kicks. Big smiles. A love of movement.'),
 'school-sports-coaching': ('School sports & coaching', 'Great coaching, built around your school.'),
 'holiday-programmes': ('Holiday programmes', 'School’s out. Time to get moving.'),
 'coach-development': ('Coach development', 'Keep learning. Make a bigger difference.')
}
ALTS = {'early-years':'A young child enjoying a football kick on the grass', 'school':'A school football team and coaches together on the pitch', 'development':'Young football players and their coaches beside a goal', 'holiday':'Children and coaches together at a Proteus school sports programme', 'team':'The Proteus coaching team together beside their branded vehicle', 'community':'Children choosing sports equipment for an activity'}

def image(name, cls='', eager=False):
    return f'<img class="{cls}" src="/assets/{name}.webp" alt="{ALTS[name]}" loading="{"eager" if eager else "lazy"}" decoding="async"'+(' fetchpriority="high"' if eager else '')+'>'

def button(text, href, cls='button-primary'):
    return f'<a class="button {cls}" href="{esc(href, quote=True)}">{text}{ARROW}</a>'

def header(active=''):
    links = [('Programmes','/programmes/'), ('Our approach','/about/'), ('Our people','/about/#team'), ('Contact','/contact/')]
    nav = ''.join(f'<a href="{url}"'+(' aria-current="page"' if name==active else '')+f'>{name}</a>' for name,url in links)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
    <div class="announcement"><span class="status-dot"></span> THE NEXT CHAPTER STARTS HERE <a href="/academy/">2027 Academy expressions of interest {ARROW}</a></div>
    <header class="site-header"><div class="header-inner"><a class="brand" href="/" aria-label="Proteus Sports Group home"><img src="/assets/logo.png" alt="Proteus Sports Group" width="225" height="68"></a><nav class="desktop-nav" aria-label="Main navigation">{nav}</nav>{button('Find your programme','/programmes/','button-small')}<button id="menu-toggle" class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span></button></div><nav id="mobile-menu" class="mobile-menu" aria-label="Mobile navigation" hidden>{nav}<a href="/academy/">2027 Academy {ARROW}</a></nav></header>'''

def footer():
    return f'''<footer class="site-footer"><div class="container footer-top"><a href="/" class="brand footer-brand" aria-label="Proteus Sports Group home"><img src="/assets/logo.png" alt="Proteus Sports Group" width="225" height="68"></a><p>Quality coaching.<br>Stronger communities.</p><div><span class="footer-label">START A CONVERSATION</span><a class="footer-email" href="mailto:info@proteus.nz">info@proteus.nz {ARROW}</a><span>Christchurch, New Zealand</span></div></div><div class="container footer-bottom"><span>© 2026 Proteus Sports Group</span><nav aria-label="Footer navigation"><a href="/programmes/">Programmes</a><a href="/contact/">Contact</a><a href="https://www.instagram.com/proteussportsgroup/" target="_blank" rel="noopener noreferrer">Instagram {ARROW}</a><a href="https://nz.linkedin.com/company/proteus-sports-group" target="_blank" rel="noopener noreferrer">LinkedIn {ARROW}</a><a href="/privacy-and-cookie-policy/">Privacy</a></nav></div></footer>'''

def asset_url(name):
    return '/'+name+'?v='+sha256((OUT/name).read_bytes()).hexdigest()[:12]

def layout(title, desc, body, active='', route='/', indexable=True):
    robots = 'index,follow' if indexable else 'noindex,follow'
    return f'''<!doctype html><html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Proteus Sports Group</title><meta name="description" content="{esc(desc,quote=True)}"><meta name="theme-color" content="#35175c"><meta name="robots" content="{robots}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="canonical" href="{ORIGIN}{route}"><meta property="og:title" content="{esc(title,quote=True)} | Proteus Sports Group"><meta property="og:description" content="{esc(desc,quote=True)}"><meta property="og:type" content="website"><meta property="og:image" content="{ORIGIN}/assets/team.jpg"><link rel="preload" href="/assets/fonts/headline.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="{asset_url('styles.css')}"><link rel="stylesheet" href="{asset_url('motion.css')}"><script src="{asset_url('app.js')}" defer></script><script src="{asset_url('motion.js')}" defer></script></head><body class="{'home-immersive' if route=='/' else ''}">{header(active)}<main id="main">{body}</main>{footer()}</body></html>'''

def faq(limit=None):
    items = DATA['faq'][:limit]
    return '<div class="faq-list">'+''.join(f'<details><summary>{esc(x["question"])}<span aria-hidden="true">+</span></summary><p>{esc(x["answer"])}</p></details>' for x in items)+'</div>'

def cards():
    result=[]
    # A deliberate progression from first experiences to development and support.
    order=[2,0,3,4,1,5]
    for n,i in enumerate(order,1):
        p=DATA['programmes'][i]; slug=p['slug']; title,caption=SHORT[slug]
        audience='players' if i in [0,1,4] else 'schools' if i in [2,3] else 'coaches'
        if i==0: audience+=' schools'
        if i==4: audience+=' schools'
        result.append(f'''<article class="programme-card {'academy-card' if i==1 else ''}" data-programme-card data-audience="{audience}"><a href="/{slug}/" class="card-link"><div class="card-image">{image(IMAGES[slug])}<span class="card-number">0{n}</span><span class="card-arrow" aria-hidden="true">↗</span>{'<span class="card-tag">2027 INTAKE</span>' if i==1 else ''}</div><div class="card-body"><h3>{esc(title)}</h3><p>{esc(caption)}</p></div></a></article>''')
    return ''.join(result)

def cta(title='Your next chapter<br>starts with a conversation.',text='A player with a goal? A school with a plan? Let’s make it happen together.'):
    return f'<section class="cta-section"><div class="container cta-inner"><div><p class="eyebrow">LET’S GET STARTED</p><h2>{title}</h2><p>{text}</p></div>{button("Talk to our team", "/contact/", "button-lime")}</div></section>'

def programmes():
    return f'''<section class="page-intro"><div class="container"><p class="eyebrow">OUR PROGRAMMES</p><h1>FIND YOUR<br><span>NEXT STEP.</span></h1><p>From first kicks to focused development. Quality coaching for players, schools, clubs and the people who coach them.</p></div></section><section class="section programme-section"><div class="container"><div class="filter-bar"><div class="programme-filters" data-programme-filters role="group" aria-label="Filter programmes"><button data-filter="all" aria-pressed="true">All programmes</button><button data-filter="players" aria-pressed="false">For players</button><button data-filter="schools" aria-pressed="false">For schools & clubs</button><button data-filter="coaches" aria-pressed="false">For coaches</button></div><span id="programme-count" aria-live="polite">6 programmes</span></div><div class="programme-grid">{cards()}</div><p id="programmes-empty" hidden>No programmes match this filter. Our team can help you find an option.</p></div></section>{cta('NOT SURE WHERE<br>TO START?', 'Tell us a little about your goals. We’ll help you find the right fit.')}'''

def programme(p):
    slug=p['slug']; is_academy=slug=='academy'; img=IMAGES[slug]
    features=''.join(f'<article><span>0{i}</span><h3>{esc(f["title"])}</h3><p>{esc(f["text"])}</p></article>' for i,f in enumerate(p['features'],1))
    if is_academy:
        contacts='<div class="academy-contacts">'+''.join(f'<a href="/contact/?interest={quote("Academy — "+c["label"].lower())}"><span>{esc(c["label"])}</span><h3>Express your interest {ARROW}</h3><p>{esc(c["email"])}</p></a>' for c in p['contacts'])+'</div>'
        extra=f'<section class="section"><div class="container"><p class="eyebrow">TAKE THE FIRST STEP</p><h2>YOUR JOURNEY.<br><span class="text-purple">LET’S TALK.</span></h2><p class="measure">{esc(p["enquiryGuidance"])}</p>{contacts}</div></section>'
    else: extra=''
    return f'''<section class="detail-hero"><div class="detail-copy"><a class="back-link" href="/programmes/">← All programmes</a><p class="eyebrow">{esc(p['eyebrow'])}</p><h1>{esc(p['title'])}</h1><p>{esc(p['intro'])}</p>{button(esc(p['cta']),'/contact/?programme='+quote(p['title']),'button-lime')}</div><div class="detail-photo">{image(img,eager=True)}<span class="image-caption">THE PROTEUS WAY / {'2027 ACADEMY' if is_academy else 'QUALITY COACHING'}</span></div></section><section class="section"><div class="container"><div class="detail-intro"><p class="eyebrow">WHO IT’S FOR</p><h2>{esc(p['audience'])}</h2></div><div class="detail-features">{features}</div></div></section>{extra}<section class="detail-next"><div class="container"><div><p class="eyebrow">LET’S MAKE A PLAN</p><h2>{esc(p['cta'])}.</h2><p>Talk to our team about options, availability and the next steps.</p></div>{button('Start a conversation','/contact/?programme='+quote(p['title']),'button-primary')}</div></section><section class="section faq-section"><div class="container faq-grid"><div><p class="eyebrow">HERE TO HELP</p><h2>GOOD<br><span class="text-purple">QUESTIONS.</span></h2></div>{faq()}</div></section>'''

def about():
    team=''.join(f'<article class="team-person"><span class="person-initials" aria-hidden="true">{"".join(n[0] for n in p["name"].split())}</span><p class="eyebrow">{esc(p["role"])}</p><h3>{esc(p["name"])}</h3><p>{esc(p["text"])}</p>'+ (f'<a class="text-link" href="mailto:{p["email"]}">Say hello {ARROW}</a>' if p.get('email') else '') + '</article>' for p in DATA['team'])
    return f'''<section class="page-intro"><div class="container"><p class="eyebrow">WE’RE PROTEUS SPORTS GROUP</p><h1>SPORT BRINGS<br><span>US TOGETHER.</span></h1><p>Our goal is simple: make sport accessible and enjoyable for everyone. We’re a Christchurch coaching team that cares about the people as much as the game.</p></div></section><div class="about-banner">{image('team',eager=True)}<span>QUALITY COACHING. STRONGER COMMUNITIES.</span></div><section class="section"><div class="container intro-grid"><p class="eyebrow">WHY WE DO IT</p><div><h2>IT STARTS WITH<br><span class="text-purple">A GREAT EXPERIENCE.</span></h2><div class="two-col-copy"><p>A positive first experience can open up a lifetime of sport. A thoughtful coach can give a player the confidence to try again. A shared game can bring a community closer.</p><p>That’s what drives us. We partner with preschools, schools, clubs and community organisations to deliver coaching that helps people participate, develop and enjoy being active.</p></div></div></div></section><section class="section about-values"><div class="container"><p class="eyebrow">THE PROTEUS WAY</p><div class="principles"><article><span>01 / SIMPLICITY</span><h3>Make it easy.</h3><p>Clear communication and end-to-end coaching support, built around what your people need.</p></article><article><span>02 / QUALITY</span><h3>Make it count.</h3><p>Professional coaches who bring purpose, energy and care to their sessions.</p></article><article><span>03 / COMMUNITY</span><h3>Make it for everyone.</h3><p>Welcoming sporting environments that encourage connection and participation.</p></article></div></div></section><section class="section" id="team"><div class="container"><div class="section-heading"><div><p class="eyebrow">OUR PEOPLE</p><h2>THE PEOPLE<br><span class="text-purple">IN YOUR CORNER.</span></h2></div><p>A shared love of sport.<br>A commitment to helping others grow.</p></div><div class="team-grid">{team}</div><div class="join-team"><div><p class="eyebrow">BRING YOUR ENERGY</p><h3>Your next step could be coaching.</h3><p>Interested in joining the Proteus team? We’d love to hear from you.</p></div>{button('Explore coaching opportunities','/contact/?interest=Coaching%20opportunities','button-secondary')}</div></div></section>{cta()}'''

def contact():
    interests=['General enquiry','Individual & Performance Coaching','Proteus Academy','Academy — football','Academy — basketball','Early Years & Fundamentals','School Sports & Coaching','Holiday Programmes','Coach Development','Club coaching','Community programmes','Active Age Programme','Teacher Aid','Coaching opportunities']
    opts=''.join(f'<option value="{esc(x,quote=True)}">{esc(x)}</option>' for x in interests)
    return f'''<section class="page-intro contact-intro"><div class="container"><p class="eyebrow">GET IN TOUCH</p><h1>LET’S MAKE<br><span>IT HAPPEN.</span></h1><p>Tell us what you have in mind. We’ll help you find the right programme, people and next step.</p></div></section><section class="section contact-section"><div class="container contact-grid"><aside class="contact-details"><p class="eyebrow">A CONVERSATION IS A GOOD START</p><h2>YOUR GOALS.<br>OUR TEAM.</h2><a class="contact-email" href="mailto:info@proteus.nz">info@proteus.nz {ARROW}</a><p>Based in Christchurch, New Zealand.<br>Working with players, schools, clubs<br>and communities.</p><div class="contact-people"><a href="mailto:patrick@proteus.nz"><span>COACHING & SCHOOL PROGRAMMES</span><strong>Paddy Rousse {ARROW}</strong><span>patrick@proteus.nz</span></a><a href="mailto:oliver@proteus.nz"><span>ACADEMY FOOTBALL & HOLIDAYS</span><strong>Oliver Hawkins {ARROW}</strong><span>oliver@proteus.nz</span></a><a href="mailto:isaac@proteus.nz"><span>ACADEMY BASKETBALL</span><strong>Isaac Rockell {ARROW}</strong><span>isaac@proteus.nz</span></a></div></aside><div class="enquiry-panel"><h3>Start your enquiry</h3><p>Prepare a message below, then open it in your email app to send to our team.</p><noscript><p>Please email <a href="mailto:info@proteus.nz">info@proteus.nz</a> or use our existing contact form below. The email preview needs JavaScript.</p></noscript><form id="enquiry-form" action="mailto:info@proteus.nz" method="post" enctype="text/plain"><div class="form-row"><div class="field"><label for="enquiry-name">Your name <span>(required)</span></label><input id="enquiry-name" name="name" autocomplete="name" required maxlength="100" placeholder="First and last name"></div><div class="field"><label for="enquiry-address">Email address <span>(required)</span></label><input id="enquiry-address" name="email" type="email" autocomplete="email" required maxlength="200" placeholder="you@example.com"></div></div><div class="field"><label for="enquiry-interest">I’m interested in</label><select id="enquiry-interest" name="interest">{opts}</select></div><div class="field"><label for="enquiry-message">What do you have in mind? <span>(required)</span></label><textarea id="enquiry-message" name="message" rows="6" required maxlength="5000" placeholder="Tell us about your goals, sport, school, club or group…"></textarea></div><button class="button button-primary" type="submit">Prepare enquiry {ARROW}</button><p class="form-note">Your message is only sent when you send the email from your email app.</p></form><div id="enquiry-preview" class="enquiry-preview" hidden><p class="eyebrow">YOUR ENQUIRY IS READY TO REVIEW</p><h3>One more step: send your email.</h3><label for="enquiry-summary">Your prepared message</label><textarea id="enquiry-summary" rows="9" readonly></textarea><div class="button-row"><a id="enquiry-email" class="button button-primary" href="mailto:info@proteus.nz">Open email draft {ARROW}</a><button id="copy-enquiry" class="button button-secondary" type="button">Copy message</button></div><p id="copy-status" role="status" aria-live="polite"></p></div><div class="contact-alternative"><p>Prefer an online form?</p><a class="text-link" href="{LEGACY_ORIGIN}/contact-1" target="_blank" rel="noopener noreferrer">Use our existing contact form {ARROW}</a></div></div></div></section><section class="section faq-section"><div class="container faq-grid"><div><p class="eyebrow">BEFORE YOU GET IN TOUCH</p><h2>GOOD<br><span class="text-purple">QUESTIONS.</span></h2></div>{faq()}</div></section>'''

def write(route,title,desc,body,active=''):
    PUBLIC_ROUTES.append(route)
    folder=OUT / route.strip('/'); folder.mkdir(parents=True,exist_ok=True)
    (folder/'index.html').write_text(layout(title,desc,body,active,route))

write('/','Sports coaching in Christchurch','Quality sports coaching for players, preschools, schools, clubs and communities. Explore Proteus programmes and the 2027 football and basketball Academy.',render_home(image,button,faq,cta,DATA,ARROW))
write('/programmes/','Find your programme','Explore individual coaching, school sport, early years, holiday programmes, coach development and the Proteus Academy.',programmes(),'Programmes')
write('/about/','Our approach & people','Meet the Christchurch coaching team behind Proteus Sports Group. Simplicity, quality and community in every sporting experience.',about(),'Our approach')
write('/contact/','Get in touch','Talk to the Proteus Sports Group team about sports coaching, school programmes, the Academy and opportunities in Christchurch.',contact(),'Contact')
for p in DATA['programmes']:
    write('/'+p['slug']+'/',p['title'],p['intro'],programme(p),'Programmes')
(OUT/'404.html').write_text(layout('Page not found','Find your way back to Proteus Sports Group.',f'<section class="page-intro"><div class="container"><p class="eyebrow">404 / A LITTLE OFF THE PITCH</p><h1>LET’S GET YOU<br><span>BACK IN PLAY.</span></h1><p>We couldn’t find that page. Our programmes are a good place to start.</p>{button("Explore programmes","/programmes/","button-primary")}</div></section>', indexable=False))
(OUT/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#35175c"/><text x="32" y="46" text-anchor="middle" font-family="Arial,sans-serif" font-size="44" font-weight="bold" fill="#d7ef70">P</text></svg>')
# Search engines may index current pages; saved designs stay out of search.
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /approved-v1/\nDisallow: /approved-v2/\nDisallow: /approved-v3/\n\nSitemap: '+ORIGIN+'/sitemap.xml\n')



# Carry the existing Proteus policy into the standalone site.
policy = (ROOT/'privacy_content.html').read_text()
policy_intro = '<div class="policy-context"><p>This is the existing Proteus Sports Group privacy and cookies policy, covering our website and linked services. Our enquiry builder prepares an email draft on your device; you send it through your email app, or use the linked online contact service.</p></div>'
write('/privacy-and-cookie-policy/', 'Privacy and cookies policy', 'Proteus Sports Group privacy and cookies policy, including how to contact our team.', '<section class="section"><article class="container policy-article">'+policy_intro+policy+'</article></section>')

# Preserve the former Squarespace entry points while canonical pages use the new routes.
LEGACY_REDIRECTS = {
    '/home': '/',
    '/contact-1': '/contact/',
    '/preschool': '/early-years-fundamentals/',
    '/first-kicks': '/early-years-fundamentals/',
    '/schools-sports': '/school-sports-coaching/',
    '/football-in-schools': '/school-sports-coaching/',
    '/football-11': '/individual-performance-coaching/',
    '/coaching': '/contact/?interest=Coaching%20opportunities',
    '/cookies-policy': '/privacy-and-cookie-policy/#cookies-policy',
}
redirect_rules = []
for old, target in LEGACY_REDIRECTS.items():
    folder = OUT/old.strip('/'); folder.mkdir(parents=True, exist_ok=True)
    destination = esc(target, quote=True)
    (folder/'index.html').write_text('<!doctype html><html lang="en-NZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0;url='+destination+'"><link rel="canonical" href="'+esc(ORIGIN+target.split('#')[0],quote=True)+'"><title>Continue to Proteus Sports Group</title></head><body><p>This page has moved. <a href="'+destination+'">Continue to Proteus Sports Group</a>.</p></body></html>')
    redirect_rules.extend([old+' '+target+' 301', old+'/ '+target+' 301'])
(OUT/'_redirects').write_text('\n'.join(redirect_rules)+'\n')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+xml_escape(ORIGIN+route)+'</loc></url>\n' for route in PUBLIC_ROUTES)+'</urlset>\n')
print(f'Built {len(PUBLIC_ROUTES)} canonical pages, {len(LEGACY_REDIRECTS)} legacy routes and saved snapshots.')
