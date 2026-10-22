"""Self-contained animated showcase using the original public-site screenshots."""
import base64


def render_showcase(root):
    def image(name):
        return 'data:image/png;base64,' + base64.b64encode((root/'assets'/name).read_bytes()).decode()

    styles = '''
text{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
@keyframes camera{0%,43%,100%{transform:translate(0,0) scale(1)}22%{transform:translate(-11px,-6px) scale(1.028)}65%,88%{transform:translate(-7px,-5px) scale(1.02)}}
@keyframes change{0%,40%{clip-path:inset(0 100% 0 0)}49%,88%{clip-path:inset(0)}98%,100%{clip-path:inset(0 0 0 100%)}}
@keyframes labelA{0%,40%,98%,100%{opacity:1}46%,94%{opacity:0}}
@keyframes labelB{0%,43%,96%,100%{opacity:0}49%,88%{opacity:1}}
@keyframes progress{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes trace{from{stroke-dashoffset:900}to{stroke-dashoffset:0}}
@keyframes lift{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}
.camera{animation:camera 14s cubic-bezier(.45,0,.55,1) infinite;transform-origin:450px 350px}
.scene-b{animation:change 14s cubic-bezier(.76,0,.24,1) infinite;clip-path:inset(0 100% 0 0)}
.label-a{animation:labelA 14s linear infinite}.label-b{animation:labelB 14s linear infinite;opacity:0}
.progress{transform-box:fill-box;transform-origin:left;animation:progress 14s linear infinite}
.trace{stroke-dasharray:160 740;animation:trace 8s linear infinite}
.status{animation:lift 3s ease-in-out infinite}
@media(prefers-reduced-motion:reduce){*{animation:none!important}.scene-b,.label-b{display:none!important}.label-a{opacity:1!important}}
'''
    body = f'''<defs>
      <linearGradient id="ink" x2="1" y2="1"><stop stop-color="#0f1725"/><stop offset=".6" stop-color="#0d1117"/><stop offset="1" stop-color="#17152c"/></linearGradient>
      <linearGradient id="accent"><stop stop-color="#69baff"/><stop offset="1" stop-color="#987eff"/></linearGradient>
      <clipPath id="screen"><rect x="22" y="142" width="856" height="481.5" rx="2"/></clipPath>
    </defs>
    <rect x="1" y="1" width="898" height="687" rx="10" fill="url(#ink)" stroke="#303a4e"/>
    <text x="24" y="30" fill="#94a7c3" font-size="10" letter-spacing="2">SELECTED PROJECT / 01</text>
    <text x="24" y="75" fill="#eef2f8" font-size="36" font-weight="650" style="font-family:Arial,sans-serif;letter-spacing:-1px">EdBrix Studios</text>
    <text x="25" y="98" fill="#a9b4c6" font-size="11">Strategia, design e sviluppo.</text>
    <g class="status"><rect x="727" y="49" width="147" height="30" rx="15" fill="#172238" stroke="#405476"/><circle cx="742" cy="64" r="3" fill="#91bfff"/><text x="753" y="68" fill="#d2e4ff" font-size="10">ESPLORA IL SITO</text></g>
    <rect x="21" y="117" width="858" height="507" rx="5" fill="#080b10" stroke="#34415a"/>
    <circle cx="34" cy="130" r="2.5" fill="#ff5f57"/><circle cx="44" cy="130" r="2.5" fill="#febc2e"/><circle cx="54" cy="130" r="2.5" fill="#28c840"/>
    <text x="450" y="134" fill="#9caabd" font-size="9" text-anchor="middle">edbrixstudios.vercel.app</text>
    <g clip-path="url(#screen)"><g class="camera">
      <image x="22" y="142" width="856" height="481.5" xlink:href="{image('edbrix-home.png')}"/>
      <g class="scene-b"><image x="22" y="142" width="856" height="481.5" xlink:href="{image('edbrix-method.png')}"/></g>
    </g></g>
    <path class="trace" d="M23 624H877" stroke="url(#accent)" stroke-width="1.5" fill="none"/>
    <g class="label-a"><text x="24" y="653" fill="#d4deed" font-size="12">01 / Identità digitale</text><text x="24" y="674" fill="#8f9bb0" font-size="9">Home · schermata del sito</text></g>
    <g class="label-b"><text x="24" y="653" fill="#d4deed" font-size="12">02 / Il metodo EdBrix</text><text x="24" y="674" fill="#8f9bb0" font-size="9">Dalla visione all’evoluzione · schermata del sito</text></g>
    <rect x="601" y="652" width="270" height="2" fill="#2d3548"/>
    <rect class="progress" x="601" y="652" width="270" height="2" fill="url(#accent)"/>
    <text x="871" y="674" fill="#8f9bb0" font-size="9" text-anchor="end">TOUR VISIVO / 14 s</text>'''
    content = f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="900" height="689" viewBox="0 0 900 689" role="img"><title>EdBrix Studios: tour animato di due schermate reali del sito pubblico</title><style>{styles}</style>{body}</svg>'
    (root/'assets/github/edbrix-showcase.svg').write_text(content)
    defs = body[:body.index('</defs>')+7]
    scene = body[body.index('<g clip-path="url(#screen)">'):body.index('<path class="trace"')]
    mobile = defs + f'''<rect x="1" y="1" width="418" height="403" rx="8" fill="url(#ink)" stroke="#303a4e"/>
    <text x="16" y="25" fill="#94a7c3" font-size="9" letter-spacing="1.5">SELECTED PROJECT / 01</text>
    <text x="16" y="61" fill="#eef2f8" font-size="28" font-weight="650" style="font-family:Arial,sans-serif;letter-spacing:-1px">EdBrix Studios</text>
    <text x="16" y="82" fill="#a9b4c6" font-size="10">Strategia, design e sviluppo.</text>
    <rect x="11" y="102" width="398" height="245" rx="4" fill="#080b10" stroke="#34415a"/>
    <text x="210" y="117" fill="#9caabd" font-size="8" text-anchor="middle">edbrixstudios.vercel.app</text>
    <g transform="translate(12 123) scale(0.4626168224) translate(-22 -142)">{scene}</g>
    <g class="label-a"><text x="16" y="370" fill="#d4deed" font-size="11">01 / Identità digitale</text></g>
    <g class="label-b"><text x="16" y="370" fill="#d4deed" font-size="11">02 / Il metodo EdBrix</text></g>
    <text x="16" y="390" fill="#8f9bb0" font-size="9">TOUR VISIVO / 14 s</text>
    <rect class="progress" x="260" y="365" width="140" height="2" fill="url(#accent)"/>
    <text x="400" y="390" fill="#d2e4ff" font-size="9" text-anchor="end">ESPLORA IL SITO</text>'''
    (root/'assets/github/edbrix-showcase-mobile.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="420" height="405" viewBox="0 0 420 405" role="img"><title>EdBrix Studios: tour di due schermate reali</title><style>{styles}</style>{mobile}</svg>')
