#!/usr/bin/env python3
"""Generate terminal-style profile SVGs from the existing public snapshot."""
import base64
import html
import json
import math
from build_edbrix import render_showcase
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/github'
DATA = json.loads((ROOT / 'data/profile.json').read_text())
ROWS = json.loads((ROOT / 'data/ascii-rows.json').read_text())
END = date.fromisoformat(DATA['updated_at'][:10])
# GitHub's calendar includes a partial extra week; derived stats use the last 365 days.
DAYS = [d for d in DATA['contributions']['days'] if END-timedelta(days=364) <= date.fromisoformat(d['date']) <= END]
BG, PANEL, BORDER, FG, MUTED, GREEN = '#0d1117','#0d1117','#30363d','#e6edf3','#919ba7','#3fb950'
MONTHS = ['gen','feb','mar','apr','mag','giu','lug','ago','set','ott','nov','dic']
CSS = '''text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-variant-numeric:tabular-nums}
@keyframes appear{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:translateY(0)}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes reveal{from{clip-path:inset(0 0 100% 0)}to{clip-path:inset(0)}}
@keyframes hide{to{opacity:0}}
@keyframes count{from{transform:translateY(0)}to{transform:translateY(-170px)}}
.counter{animation:count 1.2s steps(5,end) .7s both}
@keyframes blink{50%{opacity:0}}
@keyframes signal{0%,100%{opacity:.18}45%{opacity:1}75%{opacity:.5}}
@keyframes equalize{0%,100%{transform:scaleY(.35)}40%{transform:scaleY(1)}75%{transform:scaleY(.6)}}
.signal{animation:signal 4s ease-in-out infinite}
.equalizer{transform-box:fill-box;transform-origin:bottom;animation:equalize 3s ease-in-out infinite}
.enter{animation:appear .35s cubic-bezier(.22,1,.36,1) both}
.bar{transform-box:fill-box;transform-origin:bottom;animation:grow .8s cubic-bezier(.22,1,.36,1) both}
.ascii{animation:reveal 3.4s steps(46,end) .25s both}
.color{animation:hide .8s 4.5s both}
.cursor{animation:blink 1s steps(1) 6}
@media(prefers-reduced-motion:reduce){*{animation:none!important}.counter{transform:translateY(-170px)}.color{display:none!important}.ascii{clip-path:none!important}}
'''

def text(x,y,value,size=12,fill=FG,extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{html.escape(str(value))}</text>'

def box(x,y,w,h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{PANEL}" stroke="{BORDER}"/>'

def svg(w,h,body,label):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(label)}</title><style>{CSS}</style><rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>'

def command(w,y,label):
    return text(w/2,y,'bernindo@github ~ $ '+label,15,FG,'text-anchor="middle" font-weight="600"')

def titlebar(x,y,w,label):
    b=''
    for i,c in enumerate(['#ff5f57','#febc2e','#28c840']):
        b+=f'<circle cx="{x+13+i*10}" cy="{y+14}" r="2.5" fill="{c}"/>'
    return b+text(x+w/2,y+18,label,10,MUTED,'text-anchor="middle"')+f'<path d="M{x} {y+29}h{w}" stroke="{BORDER}"/>'

# Actual contributions; animation only changes visibility, never the recorded level.
b=command(900,24,'./contributions.sh')
all_days=DATA['contributions']['days']
first=date.fromisoformat(all_days[0]['date'])
last_month=None
palette=['#161b22','#0e4429','#006d32','#26a641','#39d353']
for i,d in enumerate(all_days):
    day=date.fromisoformat(d['date']); col,row=divmod((day-first).days,7)
    x,y=46+col*15.7,65+row*15.7
    if (day.month!=last_month) and day.day<=7:
        if col<51: b+=text(x,52,MONTHS[day.month-1],9,MUTED)
        last_month=day.month
    b+=f'<rect class="enter" style="animation-delay:{(col+row)*.027:.3f}s" x="{x:.1f}" y="{y:.1f}" width="12" height="12" rx="2" fill="{palette[min(4,d["level"])]}" stroke="#26312b" stroke-width=".35"><title>{d["date"]}: {d["count"]} contributi</title></rect>'
for row,label in [(1,'lun'),(3,'mer'),(5,'ven')]: b+=text(8,74+row*15.7,label,9,MUTED)
b+=text(46,195,f'{DATA["contributions"]["total"]} contributi nell’ultimo anno',12,FG)
b+=text(735,195,'meno',9,MUTED)
for i,c in enumerate(palette): b+=f'<rect x="{767+i*16}" y="185" width="11" height="11" rx="2" fill="{c}"/>'
b+=text(852,195,'più',9,MUTED)
(OUT/'terminal-calendar.svg').write_text(svg(900,214,b,'Calendario animato dei contributi pubblicamente visibili di bernindo'))

# Dense abstract motion graphic. It does not encode contributions or dates.
b=command(900,24,'./signal.sh')
for col in range(53):
    for row in range(7):
        phase = math.sin(col*.32+row*.8) + math.cos(col*.17-row*.5)
        level=max(1,min(4,int((phase+2)/4*4)+1))
        x,y=34+col*15.7,51+row*15.7
        b+=f'<rect class="signal" style="animation-delay:{-(col*.08+row*.11):.2f}s" x="{x:.1f}" y="{y:.1f}" width="12" height="12" rx="2" fill="{palette[level]}"/>'
b+=text(34,183,'MATRICE ANIMATA / DECORATIVA',11,'#7ee787')
b+=text(34,202,'Non rappresenta contributi GitHub. Statistiche reali nella sezione sotto.',10,MUTED)
(OUT/'terminal-signal.svg').write_text(svg(900,216,b,'Matrice animata decorativa: non rappresenta contributi GitHub'))

# Streaks and histogram calculated only from the recorded public days.
longest=run=0
for d in DAYS:
    run=run+1 if d['count'] else 0
    longest=max(longest,run)
current=0
cursor=len(DAYS)-1
if cursor>=0 and DAYS[cursor]['count']==0: cursor-=1
while cursor>=0 and DAYS[cursor]['count']>0:
    current+=1; cursor-=1
active=sum(d['count']>0 for d in DAYS)
best=max((d['count'] for d in DAYS),default=0)
avg=sum(d['count'] for d in DAYS)/active if active else 0
monthly=defaultdict(int)
for d in DAYS: monthly[d['date'][:7]]+=d['count']
keys=[]
for i in range(11,-1,-1):
    n=END.year*12+END.month-1-i
    keys.append(f'{n//12:04d}-{n%12+1:02d}')
# Twelve displayed calendar months; the first and current month may be partial.
values=[monthly[k] for k in keys]
metrics=[('streak attuale',current,'giorni consecutivi'),('streak più lunga',longest,'ultimi 365 giorni'),('contributi',DATA['contributions']['total'],'totale annuo GitHub'),('giorni attivi',active,'ultimi 365 giorni'),('giorno migliore',best,'contributi in un giorno'),('media / giorno attivo',f'{avg:.1f}','contributi')]

# Edge density from the supplied ASCII grid. No generated or substituted portrait.
ramp=' .:-=+*#%@'
levels=[[ramp.find(c) if c in ramp else 0 for c in row] for row in ROWS]
outline=[]
for y,row in enumerate(levels):
    out=''
    for x,v in enumerate(row):
        neighbors=[levels[yy][xx] for yy,xx in [(max(0,y-1),x),(min(len(levels)-1,y+1),x),(y,max(0,x-1)),(y,min(len(row)-1,x+1))]]
        e=max(abs(v-n) for n in neighbors)
        out += ' ' if v==0 and e<2 else ' .:+=*#%@'[min(8,e)]
    outline.append(out)

photo='data:image/png;base64,'+base64.b64encode((ROOT/'assets/bernardo.png').read_bytes()).decode()

def dashboard(mobile=False, stats=True):
    w=420 if mobile else 900
    px,py,pw,ph=(4,53,412,395) if mobile else (4,53,382,420)
    sx,sy,sw=(4,466,412) if mobile else (400,53,496)
    h=895 if mobile else 491
    body=command(w,26,'whoami')+box(px,py,pw,ph)+titlebar(px,py,pw,'portrait.ascii')
    # Color portrait is visible during the introductory scan, then the ASCII outline remains.
    size=330; ix=px+(pw-size)/2; iy=py+51
    body+=f'<defs><clipPath id="portrait"><circle cx="{ix+size/2}" cy="{iy+size/2}" r="{size/2}"/></clipPath></defs>'
    body+=f'<g class="color" clip-path="url(#portrait)"><image x="{ix}" y="{iy}" width="{size}" height="{size}" xlink:href="{photo}"/></g>'
    body+=f'<g class="ascii"><rect x="{ix}" y="{iy}" width="{size}" height="{size}" fill="{BG}"/>'
    # A solid backing makes the printing ASCII readable while the color image fades.
    for i,row in enumerate(outline):
        body+=text(ix+4,iy+9+i*6.8,row,6.8,'#c9d1d9','xml:space="preserve" textLength="322" lengthAdjust="spacingAndGlyphs"')
    body+='</g>'+text(px+15,py+ph-17,'Bernardo / @bernindo',11,MUTED)
    body+=box(sx,sy,sw,420)+titlebar(sx,sy,sw,'public-stats.sh' if stats else 'edbrix-studios.sh')
    if not stats:
        info=[('progetto','EdBrix Studios'),('framework','Next.js'),('interfaccia','React'),('linguaggio','TypeScript'),('animazioni','GSAP'),('grafica 3D','Three.js')]
        cw=(sw-30)/2
        for i,(label,value) in enumerate(info):
            x=sx+10+(i%2)*(cw+10); y=sy+39+(i//2)*78
            body+=f'<g class="enter" style="animation-delay:{.3+i*.12}s"><rect x="{x}" y="{y}" width="{cw}" height="70" rx="3" fill="#10161d" stroke="#212830"/>'
            body+=text(x+11,y+21,'$ '+label,10,MUTED)+text(x+11,y+49,value,17,'#7ee787' if i==0 else FG,'font-weight="600"')+'</g>'
        x=sx+20; y=sy+292; width=sw-40
        body+=text(x,y,'$ motion equalizer / decorativo',10,MUTED)
        step=width/18
        for i in range(18):
            height=36+30*(math.sin(i*.53)+1)/2
            body+=f'<rect class="equalizer" style="animation-delay:{-i*.18:.2f}s" x="{x+step*i+2:.2f}" y="{y+88-height:.2f}" width="{step-5:.2f}" height="{height:.2f}" rx="1" fill="{GREEN}"/>'
        body+=text(x,y+108,'Effetto visivo · nessuna metrica simulata',9,MUTED)
        return svg(w,h,body,'Bernardo: ritratto ASCII, progetto EdBrix Studios e tecnologie del sito; equalizzatore decorativo')
    cw=(sw-30)/2
    for i,(label,value,note) in enumerate(metrics):
        x=sx+10+(i%2)*(cw+10); y=sy+39+(i//2)*78
        body+=f'<g class="enter" style="animation-delay:{.5+i*.12}s">'
        body+=f'<rect x="{x}" y="{y}" width="{cw}" height="70" rx="3" fill="#10161d" stroke="#212830"/>'
        body+=text(x+11,y+17,'$ '+label,10,MUTED)
        body+=f'<defs><clipPath id="count-{i}"><rect x="{x+9}" y="{y+22}" width="{cw-18}" height="29"/></clipPath></defs><g clip-path="url(#count-{i})"><g class="counter">'
        for step in range(6):
            n = float(value)*step/5
            shown = f'{n:.1f}' if isinstance(value,str) else str(int(n))
            body+=text(x+11,y+45+step*34,shown,25,GREEN if i<2 else FG,'font-weight="700"')
        body+='</g></g>'
        body+=text(x+11,y+59,note,8.5,MUTED)+'</g>'
    x=sx+20; y=sy+292; width=sw-40
    body+=text(x,y,'$ contributions / month',10,MUTED)
    maxval=max(max(values),1)
    for line in [0,0.5,1]:
        yy=y+90-line*68
        body+=f'<path d="M{x} {yy}h{width}" stroke="#212830" stroke-dasharray="2 4"/>'
    step=width/12
    for i,(k,v) in enumerate(zip(keys,values)):
        bh=v/maxval*65; bx=x+step*i+5; by=y+90-bh
        if v:
            body+=f'<rect class="bar" style="animation-delay:{1.1+i*.055}s" x="{bx:.2f}" y="{by:.2f}" width="{step-10:.2f}" height="{bh:.2f}" rx="1" fill="{GREEN}"><title>{k}: {v}</title></rect>'
            body+=text(bx+(step-10)/2,by-5,v,9,FG,'text-anchor="middle" class="enter" style="animation-delay:2s"')
        else:
            body+=f'<path d="M{bx:.2f} {y+90}h{step-10:.2f}" stroke="#3a444f"/>'
        body+=text(bx+(step-10)/2,y+106,MONTHS[int(k[5:])-1][0].upper(),9,MUTED,'text-anchor="middle"')
    return svg(w,h,body,'Bernardo: ritratto da colore ad ASCII, statistiche pubbliche reali e contributi mensili')

(OUT/'terminal-statistics.svg').write_text(dashboard())
(OUT/'terminal-dashboard.svg').write_text(dashboard(stats=False))
(OUT/'terminal-statistics-mobile.svg').write_text(dashboard(True))
(OUT/'terminal-dashboard-mobile.svg').write_text(dashboard(True,stats=False))

render_showcase(ROOT)

checks='\n'.join(f'- **{c["name"]}:** '+('sito raggiungibile (HTTP 200)' if c['reachable'] else 'raggiungibilità non confermata')+'.' for c in DATA['checks'] if c['name']=='EdBrix Studios')
events='\n'.join(f'- {e["created_at"][:10]} · {e["type"]} · {e.get("repo",{}).get("name","")}' for e in DATA['events'][:5]) or 'Nessun evento pubblico recente restituito da GitHub.'
readme=f'''<div align="center">

<img src="assets/github/terminal-signal.svg" width="900" alt="Matrice decorativa animata: non rappresenta contributi GitHub">

<picture>
  <source media="(max-width: 600px)" srcset="assets/github/terminal-dashboard-mobile.svg">
  <img src="assets/github/terminal-dashboard.svg" width="900" alt="Bernardo: ritratto ASCII, EdBrix Studios, tecnologie ed equalizzatore decorativo">
</picture>

### `bernindo@github ~ $ ./edbrix.sh`

<a href="https://edbrixstudios.vercel.app"><picture>
  <source media="(max-width: 600px)" srcset="assets/github/edbrix-showcase-mobile.svg">
  <img src="assets/github/edbrix-showcase.svg" width="900" alt="EdBrix Studios: tour animato delle schermate reali del sito. Apri il sito.">
</picture></a>

**[Esplora EdBrix Studios](https://edbrixstudios.vercel.app)**

</div>

Il tour anima due schermate del sito pubblico. Matrice ed equalizzatore sono decorativi; i dati GitHub reali sono riportati sotto.

<details><summary>Statistiche GitHub reali</summary>

![Calendario reale](assets/github/terminal-calendar.svg)

<picture>
  <source media="(max-width: 600px)" srcset="assets/github/terminal-statistics-mobile.svg">
  <img src="assets/github/terminal-statistics.svg" width="900" alt="Statistiche pubbliche reali e ritratto ASCII">
</picture>

</details>

<details><summary>Snake dei contributi</summary>

![Snake sul calendario reale](assets/github/snake.svg)

</details>

<details><summary>Dati, attività e fonti</summary>

Rilevazione: **{END.isoformat()}**. Il calendario mostra i contributi pubblicamente visibili; non rappresenta automaticamente tutta l’attività privata.

Streak, giorni attivi, giorno migliore e media sono calcolati sugli ultimi 365 giorni. La streak attuale include ieri se oggi non ci sono ancora contributi. Il grafico mostra gli ultimi 12 mesi di calendario; il mese corrente è parziale. I valori zero restano zero.

{events}

{checks}

I controlli HTTP misurano la raggiungibilità, non il funzionamento interno dei prodotti.

[Dati e fonti](data/profile.json) · [GitHub](https://github.com/bernindo)

</details>
'''
(ROOT/'README.md').write_text(readme)
(ROOT/'data/terminal-metrics.json').write_text(json.dumps({'current_streak':current,'longest_streak':longest,'active_days':active,'best_day':best,'average_active_day':avg,'months':dict(zip(keys,values))},indent=2))
# Frozen variants are for local review only, regenerated alongside the animated files.
for name in ['terminal-calendar','terminal-signal','terminal-statistics','terminal-statistics-mobile','terminal-dashboard','terminal-dashboard-mobile','edbrix-showcase','edbrix-showcase-mobile','snake']:
    p = OUT / (name+'.svg')
    frozen = p.read_text().replace('</style>', '*{animation:none!important}.counter{transform:translateY(-170px)}.color{display:none!important}.ascii{clip-path:none!important}.snake-body,.scene-b,.label-b{display:none!important}.label-a{opacity:1!important}</style>')
    (OUT/(name+'-static.svg')).write_text(frozen)
if (ROOT/'profile.html').exists():
    frozen = (ROOT/'profile.html').read_text()
    for name in ['terminal-calendar','terminal-signal','terminal-statistics','terminal-statistics-mobile','terminal-dashboard','terminal-dashboard-mobile','edbrix-showcase','edbrix-showcase-mobile','snake']:
        frozen = frozen.replace(name+'.svg',name+'-static.svg')
    (ROOT/'profile-static.html').write_text(frozen)
print('Built terminal calendar, desktop/mobile dashboard, project panels and README.')
