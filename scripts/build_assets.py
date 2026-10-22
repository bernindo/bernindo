#!/usr/bin/env python3
"""Build self-contained, script-free SVG assets and a draft GitHub README."""
import base64
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'github'
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((ROOT / 'data' / 'profile.json').read_text())
ROWS = json.loads((ROOT / 'data' / 'ascii-rows.json').read_text())
(ROOT / 'data' / 'ascii-data.js').write_text('window.ASCII_ROWS = ' + json.dumps(ROWS) + ';\n')
STAMP = DATA['updated_at'][:10]


def image(name):
    return 'data:image/png;base64,' + base64.b64encode((ROOT / 'assets' / name).read_bytes()).decode()


def svg(width, height, body, label, style=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(label, quote=True)}"><title>{html.escape(label)}</title><style>text{{font-family:monospace}}{style}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}.ascii{{display:none}}}}</style>{body}</svg>'''


def header(light=False):
    bg, fg, muted, line, accent = ('#faf8f1','#282c2c','#636d6b','#dbddd3','#99522c') if light else ('#171b1d','#f0eee6','#a1aaa9','#343b3e','#e8ad82')
    body = f'<rect width="1000" height="485" rx="20" fill="{bg}"/><path d="M0 50h1000" stroke="{line}"/>'
    for i, color in enumerate(['#d88d7a','#d8b77c','#91adae']):
        body += f'<circle cx="{25+i*14}" cy="25" r="4" fill="{color}"/>'
    body += f'<text x="95" y="29" fill="{muted}" font-size="11">bernindo / README.md</text><text x="45" y="105" fill="{accent}" font-size="11">~/ CIAO, MONDO.</text>'
    body += f'<g class="intro"><text x="42" y="187" fill="{fg}" font-size="69" letter-spacing="-4" style="font-family:sans-serif;font-weight:650">Bernardo<tspan fill="{accent}">.</tspan></text><text x="45" y="235" fill="{muted}" font-size="21" style="font-family:sans-serif">Le idee sono un buon inizio.</text><text x="45" y="264" fill="{muted}" font-size="21" style="font-family:sans-serif">Il bello è costruirle.</text></g>'
    body += f'<rect x="45" y="295" width="390" height="138" rx="12" fill="{bg}" stroke="{line}"/>'
    for i,(text,color) in enumerate([('❯ whoami',accent),('name      Bernardo',fg),('handle    @bernindo',muted),('projects  fidcard · edbrix-studios',muted)]):
        body += f'<text class="row" style="animation-delay:{.4+i*.45}s" x="65" y="{324+i*26}" font-size="13" fill="{color}">{html.escape(text)}</text>'
    body += '<defs><clipPath id="portrait"><circle cx="755" cy="252" r="166"/></clipPath></defs>'
    body += f'<circle cx="755" cy="252" r="176" fill="none" stroke="{line}"/><g clip-path="url(#portrait)"><image class="color" x="580" y="77" width="350" height="350" xlink:href="{image("bernardo.png")}"/><g class="ascii"><circle cx="755" cy="252" r="168" fill="{bg}"/>'
    for i,row in enumerate(ROWS):
        body += f'<text class="row" xml:space="preserve" x="590" y="{100+i*6.4:.1f}" font-size="6.4" fill="{accent}" style="animation-delay:{.3+i*.027:.3f}s">{html.escape(row)}</text>'
    body += f'</g></g><text x="707" y="451" fill="{muted}" font-size="10">hello, world_</text>'
    styles='@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}@keyframes out{from{opacity:1}to{opacity:0;visibility:hidden}}.intro{animation:in .8s ease both}.row{animation:in .4s ease both}.ascii{animation:out 1s 2.7s both}.color{animation:in 1s 2.5s both}'
    return svg(1000,485,body,'Bernardo, bernindo. Ritratto da ASCII a colori e presentazione.',styles)


for light in [False, True]:
    (OUT / ('header-light.svg' if light else 'header-dark.svg')).write_text(header(light))

days = DATA['contributions']['days']
start = datetime.fromisoformat(days[0]['date'])
calendar = '<rect width="866" height="168" rx="12" fill="#171b1d"/>'
contribution_word = 'contributo' if DATA['contributions']['total']==1 else 'contributi'
calendar += f'<text x="20" y="25" fill="#a1aaa9" font-size="11">{DATA["contributions"]["total"]} {contribution_word} nell’ultimo anno · rilevazione {STAMP}</text>'
points = {}
for day in days:
    index = (datetime.fromisoformat(day['date'])-start).days
    col,row = divmod(index,7)
    x,y = 24+col*15.3,43+row*15
    palette = ['#343b3e','#6e6656','#a67b55','#dba36e','#efbc89']
    calendar += f'<rect class="cell" style="animation-delay:{(col+row)*.018:.3f}s" x="{x:.1f}" y="{y}" width="11.3" height="11.3" rx="2" fill="{palette[min(day["level"],4)]}"><title>{day["date"]}: {day["count"]}</title></rect>'
    points[(col,row)] = (x+5.65,y+5.65)
path = []
for col in range((len(days)+6)//7):
    for i in range(7):
        row = 6-i if col%2 else i
        if (col,row) in points:
            path.append(points[(col,row)])
d = 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x,y in path)
style='@keyframes fade{from{opacity:0}to{opacity:1}}.cell{animation:fade .4s ease both}'
(OUT/'contributions.svg').write_text(svg(866,168,calendar,'Calendario dei contributi pubblicamente visibili',style))
snake = calendar
for i in range(5,-1,-1):
    snake += f'<circle class="snake-body" r="{5 if i==0 else 4}" fill="{"#e8ad82" if i==0 else "#a5bfd9"}" opacity="{1-i*.12:.2f}"><animateMotion dur="15s" repeatCount="indefinite" begin="{i*.05:.2f}s" path="{d}"/></circle>'
(OUT/'snake.svg').write_text(svg(866,168,snake,'Snake animato sul calendario reale dei contributi','@media(prefers-reduced-motion:reduce){.snake-body{display:none}}'))

stats=[(DATA['contributions']['total'],'contributi / anno'),(DATA['user']['public_repos'],'repository pubblici'),(DATA['user']['followers'],'follower'),(sum(r.get('stargazers_count',0) for r in DATA['repos']),'stelle / repo pubblici')]
body='<rect width="866" height="105" rx="12" fill="#171b1d"/>'
for i,(value,label) in enumerate(stats):
    x=26+i*214
    body+=f'<text x="{x}" y="51" font-size="34" fill="#f0eee6">{value}</text><text x="{x}" y="78" font-size="10" fill="#a1aaa9">{label}</text>'
(OUT/'stats.svg').write_text(svg(866,105,body,'Statistiche pubbliche di bernindo, rilevate '+STAMP))

for slug,first,second in [('fidavanti','fidavanti-home.png','fidavanti-flow.png'),('edbrix','edbrix-home.png','edbrix-method.png')]:
    body=f'<image width="1280" height="720" preserveAspectRatio="xMidYMid meet" xlink:href="{image(first)}"/><image class="second" width="1280" height="720" preserveAspectRatio="xMidYMid meet" xlink:href="{image(second)}"/>'
    style='@keyframes tour{0%,38%{opacity:0}45%,86%{opacity:1}94%,100%{opacity:0}}.second{animation:tour 12s ease-in-out infinite}@media(prefers-reduced-motion:reduce){.second{display:none}}'
    (OUT/(slug+'-demo.svg')).write_text(svg(1280,720,body,'Tour visivo del sito pubblico '+slug,style))

checks = '\n'.join(f'- **{html.escape(c["name"])}:** {"HTTP 200, sito raggiungibile" if c["reachable"] else "raggiungibilità non confermata"} ({STAMP}).' for c in DATA['checks'])
events = '\n'.join(f'- {e["created_at"][:10]} · {e["type"]} · {e.get("repo",{}).get("name","")}' for e in DATA['events'][:5]) or 'Nessun evento pubblico recente restituito da GitHub.'
readme=f'''<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/github/header-light.svg">
  <img src="assets/github/header-dark.svg" alt="Bernardo, @bernindo. Le idee sono un buon inizio. Il bello è costruirle." width="1000">
</picture>

### Progetti selezionati

**[FidAvanti / fidcard](https://www.fidavanti.it)** — Carte fedeltà digitali: iscrizione con QR, punti e premi.

[![Tour visivo del sito pubblico FidAvanti](assets/github/fidavanti-demo.svg)](https://www.fidavanti.it)

**[EdBrix Studios](https://edbrixstudios.vercel.app)** — Strategia, design e sviluppo: il sito dello studio.

[![Tour visivo del sito pubblico EdBrix Studios](assets/github/edbrix-demo.svg)](https://edbrixstudios.vercel.app)

Le sequenze mostrano schermate dei siti pubblici, non registrazioni di operazioni nelle applicazioni.

### GitHub, in numeri

![Statistiche pubbliche di bernindo](assets/github/stats.svg)

![Calendario dei contributi pubblicamente visibili](assets/github/contributions.svg)

<details><summary>Snake dei contributi</summary>

![Snake sul calendario reale](assets/github/snake.svg)

</details>

<details><summary>Attività, stato dei siti e fonti</summary>

{events}

{checks}

I controlli HTTP indicano la raggiungibilità al momento della rilevazione, non l’esito di test o CI. Dati pubblici rilevati il **{STAMP}**. Non comprendono automaticamente tutta l’attività privata.

[Dati e fonti](data/profile.json) · [Profilo GitHub](https://github.com/bernindo)

</details>
'''
(ROOT/'README.md').write_text(readme)
print('Built 7 self-contained animated/static SVG assets and draft README.md.')
