#!/usr/bin/env python3
# Builds public/index.html — HyperFrames talking-head-recut composition.
import json, html, math, os, glob
from fontTools.ttLib import TTFont
FPS=25; W=1080; H=1920; DUR=43.48
def q(t): return round(round(float(t)*FPS)/FPS,4)

# --- exact Unbounded glyph-width fitting so subtitles never clip the frame ---
_UW={}; _UPM=1000
for _p in sorted(glob.glob("public/fonts/unbounded-*.woff2")):
    _f=TTFont(_p); _UPM=_f["head"].unitsPerEm
    for _cp,_g in _f.getBestCmap().items():
        _UW.setdefault(_cp,_f["hmtx"][_g][0])
def _text_w(text,size):
    return sum(_UW.get(ord(c),_UW.get(ord('X'),600)) for c in text)/_UPM*size
USABLE=905  # 1080 - ~87px margins each side (brand wants >=70)

# ---------------- SUBTITLES (recut-relative, hand-curated) ----------------
# each: [start, end, "TEXT", [accent word indices]]
SUBS=[
 [0.10,1.42,"ТРИ ПРИЧИНЫ",[0]],
 [1.46,2.30,"СДЕЛАТЬ РЕМОНТ",[]],
 [2.30,2.92,"В ДУБАЕ",[1]],
 [2.96,3.70,"ПЕРВАЯ",[0]],
 [3.72,4.50,"КАЧЕСТВЕННЫЙ РЕМОНТ",[]],
 [4.52,5.12,"МОЖЕТ ПОВЫСИТЬ",[]],
 [5.14,5.88,"АРЕНДНУЮ СТАВКУ",[]],
 [5.90,7.54,"НА 40–60%",[1]],
 [7.56,8.14,"ТО ЕСТЬ",[]],
 [8.52,9.20,"ВАША КВАРТИРА",[]],
 [9.22,9.80,"СДАВАЛАСЬ ЗА",[]],
 [9.82,10.60,"100 000 AED",[0,1]],
 [10.62,11.28,"ПОСЛЕ РЕМОНТА",[]],
 [11.30,11.96,"СДАВАТЬСЯ ЗА",[]],
 [11.98,13.44,"140–160К AED",[0]],
 [13.54,15.08,"ВТОРОЕ",[0]],
 [15.18,15.98,"СООТВЕТСТВИЕ",[]],
 [16.00,17.64,"ПРЕМИУМ-РЫНКУ",[0]],
 [17.66,18.58,"ПОКУПАТЕЛИ",[]],
 [18.60,19.04,"В ДУБАЕ",[1]],
 [19.06,19.68,"ПРЕДПОЧИТАЮТ",[]],
 [19.70,20.28,"СОВРЕМЕННЫЕ",[]],
 [20.30,21.02,"ИНТЕРЬЕРЫ",[0]],
 [21.04,21.58,"КАЧЕСТВЕННАЯ",[]],
 [21.60,22.04,"ОТДЕЛКА",[0]],
 [22.06,22.54,"ВСТРОЕННАЯ",[]],
 [22.56,23.18,"ТЕХНИКА",[0]],
 [23.28,24.46,"ДИЗАЙН-РЕШЕНИЯ",[0]],
 [24.48,25.12,"БЕЗ РЕМОНТА",[0,1]],
 [25.14,25.88,"ВАША КВАРТИРА",[]],
 [26.28,26.98,"МОЖЕТ ЗАВИСНУТЬ",[1]],
 [27.00,27.66,"НА РЫНКЕ",[]],
 [27.68,28.30,"ОБНОВЛЁННЫЙ",[]],
 [28.32,29.20,"ОБЪЕКТ С РЕМОНТОМ",[]],
 [29.22,29.84,"СДАСТСЯ",[]],
 [29.86,30.66,"В РАЗЫ БЫСТРЕЕ",[2]],
 [30.92,31.52,"ТРЕТЬЕ",[0]],
 [31.54,32.08,"В ДУБАЕ",[1]],
 [32.10,32.78,"МНОГИЕ ОБЪЕКТЫ",[]],
 [32.80,34.04,"ПОКУПАЮТ ДЛЯ",[]],
 [34.06,34.86,"ПЕРЕПРОДАЖИ",[0]],
 [35.26,35.94,"ВАША КВАРТИРА",[]],
 [35.96,36.44,"С РЕМОНТОМ",[]],
 [36.46,37.92,"ВЫРАСТЕТ В ЦЕНЕ",[0]],
 [37.94,39.22,"НА 40–50%",[1]],
 [39.24,40.18,"ЭТО АКТУАЛЬНО",[1]],
 [40.20,41.04,"В РАЙОНАХ",[]],
 [41.06,41.86,"ПАЛЬМ-ДЖУМЕЙРА",[0]],
 [41.88,42.54,"МАРИНА",[0]],
 [42.56,43.46,"И ДАУНТАУН",[1]],
]

def fit_size(text):
    s=92
    while s>44 and _text_w(text,s)*1.03>USABLE: s-=1
    return s

def sub_html(text,acc):
    words=text.split(" ")
    parts=[]
    for i,w in enumerate(words):
        cls="acc" if i in acc else "w"
        parts.append(f'<span class="{cls}">{html.escape(w)}</span>')
    return " ".join(parts)

sub_hosts=[]; sub_tl=[]
for i,(s,e,text,acc) in enumerate(SUBS):
    s=q(s); e=q(min(e,DUR)); dur=round(e-s,4)
    if dur<=0.05: continue
    cid=f"sub-{i:02d}"; F=fit_size(text)
    sub_hosts.append(f'''<div class="card-host clip sub" id="{cid}" data-card-id="{cid}" data-start="{s:.4f}" data-duration="{dur:.4f}" data-track-index="3" style="left:0;top:1210px;width:1080px;height:300px;visibility:hidden;opacity:0;">
  <div class="subline" id="{cid}-line" style="font-size:{F}px;">{sub_html(text,acc)}</div>
</div>''')
    sub_tl.append(f'''  tl.set('.card-host[data-card-id="{cid}"]',{{visibility:"visible"}},{s:.4f});
  tl.fromTo('.card-host[data-card-id="{cid}"]',{{opacity:0}},{{opacity:1,duration:0.12,ease:"power2.out"}},{s:.4f});
  tl.fromTo('#{cid}-line',{{opacity:0,scale:0.90,rotation:-3,y:16}},{{opacity:1,scale:1,rotation:0,y:0,duration:0.22,ease:"back.out(1.9)"}},{s:.4f});
  tl.set('.card-host[data-card-id="{cid}"]',{{visibility:"hidden"}},{e:.4f});''')

# ---------------- MOTION-GRAPHIC CARDS ----------------
card_hosts=[]; card_tl=[]

def host(cid,s,e,x,y,w,h,inner,z=4):
    s=q(s); e=q(min(e,DUR)); dur=round(e-s,4)
    card_hosts.append(f'''<div class="card-host clip" id="{cid}" data-card-id="{cid}" data-start="{s:.4f}" data-duration="{dur:.4f}" data-track-index="{z}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;visibility:hidden;opacity:0;">
{inner}
</div>''')
    return s,e

def enter_exit(cid,s,e,dy=-26,d_in=0.42):
    card_tl.append(f'''  tl.set('.card-host[data-card-id="{cid}"]',{{visibility:"visible"}},{s:.4f});
  tl.fromTo('.card-host[data-card-id="{cid}"]',{{opacity:0,y:{dy}}},{{opacity:1,y:0,duration:{d_in},ease:"power3.out"}},{s:.4f});
  tl.to('.card-host[data-card-id="{cid}"]',{{opacity:0,duration:0.30,ease:"power2.in"}},{max(s+0.4,e-0.30):.4f});
  tl.set('.card-host[data-card-id="{cid}"]',{{visibility:"hidden"}},{e:.4f});''')

# C1 kicker
s,e=host("c-kicker",0.20,2.90,300,86,480,72,
 '''<div class="root pill-k"><span class="dot"></span><span class="kt">ДУБАЙ · НЕДВИЖИМОСТЬ</span></div>''',z=4)
enter_exit("c-kicker",s,e,dy=-20)

# chapter pills
def chapter(cid,s,e,num,label):
    s2,e2=host(cid,s,e,300,80,480,96,
      f'''<div class="root chap"><span class="cn">{num}</span><span class="cl">{label}</span></div>''')
    enter_exit(cid,s2,e2,dy=-22)

# stat callout with count-up
def stat(cid,s,e,to,label,prefix="+",suffix="%"):
    s2,e2=host(cid,s,e,150,150,780,290,
      f'''<div class="root statc">
   <div class="sk">{label}</div>
   <div class="sv"><span class="pre">{prefix}</span><span class="num" id="{cid}-num">0</span><span class="suf">{suffix}</span></div>
   <div class="bar" id="{cid}-bar"></div>
 </div>''')
    enter_exit(cid,s2,e2,dy=-30,d_in=0.46)
    cs=q(s2+0.30)
    card_tl.append(f'''  (function(){{var o={{v:0}};tl.to(o,{{v:{to},duration:0.95,ease:"power2.out",onUpdate:function(){{var el=document.getElementById("{cid}-num");if(el)el.textContent=Math.round(o.v);}}}},{cs:.4f});}})();
  tl.fromTo('#{cid}-bar',{{scaleX:0}},{{scaleX:1,duration:0.7,ease:"power2.out"}},{cs:.4f});''')

# C2/C5/C7 chapters
chapter("c-ch1",2.96,5.60,"01","АРЕНДНАЯ СТАВКА")
chapter("c-ch2",13.54,15.10,"02","ПРЕМИУМ-РЫНОК")
chapter("c-ch3",30.90,33.10,"03","ПЕРЕПРОДАЖА")

# C3 stat +40-60% , C8 stat +40-50%
stat("c-stat1",5.70,9.10,60,"РОСТ АРЕНДНОЙ СТАВКИ",prefix="+40–",suffix="%")
stat("c-stat2",37.90,40.15,50,"РОСТ СТОИМОСТИ",prefix="+40–",suffix="%")

# C4 money before->after
s,e=host("c-money",9.55,13.45,150,150,780,300,
 '''<div class="root money">
   <div class="mk">АРЕНДА · AED / МЕС</div>
   <div class="mrow">
     <span class="was">100 000</span>
     <span class="arr" id="c-money-arr">→</span>
     <span class="now" id="c-money-now">140–160К</span>
   </div>
 </div>''')
enter_exit("c-money",s,e,dy=-30,d_in=0.46)
mcs=q(s+0.34)
card_tl.append(f'''  tl.fromTo('#c-money-arr',{{opacity:0,x:-14}},{{opacity:1,x:0,duration:0.4,ease:"power3.out"}},{mcs:.4f});
  tl.fromTo('#c-money-now',{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.42,ease:"back.out(2)"}},{q(s+0.52):.4f});''')

# C6 checklist (reason 2 features) — mid band above subtitles
feats=["СОВРЕМЕННЫЕ ИНТЕРЬЕРЫ","ВСТРОЕННАЯ ТЕХНИКА","ДИЗАЙНЕРСКИЕ РЕШЕНИЯ"]
rows="".join(f'''<div class="frow" id="c-feat-r{j}"><span class="chk">✓</span><span class="ft">{f}</span></div>''' for j,f in enumerate(feats))
s,e=host("c-feat",19.55,25.05,120,980,840,300,f'''<div class="root feat">{rows}</div>''')
enter_exit("c-feat",s,e,dy=24,d_in=0.4)
for j in range(3):
    js=q(s+0.35+j*0.42)
    card_tl.append(f'''  tl.fromTo('#c-feat-r{j}',{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.44,ease:"power3.out"}},{js:.4f});''')

# C9 districts pills — mid band
dists=["PALM JUMEIRAH","MARINA","DOWNTOWN"]
pills="".join(f'''<div class="dpill" id="c-dist-p{j}">{d}</div>''' for j,d in enumerate(dists))
s,e=host("c-dist",40.15,43.46,90,995,900,250,f'''<div class="root dist">{pills}</div>''')
# custom enter (no early exit — hold to end)
s=q(s); e=q(min(e,DUR))
card_tl.append(f'''  tl.set('.card-host[data-card-id="c-dist"]',{{visibility:"visible"}},{s:.4f});
  tl.fromTo('.card-host[data-card-id="c-dist"]',{{opacity:0,y:22}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},{s:.4f});''')
for j in range(3):
    js=q(s+0.25+j*0.34)
    card_tl.append(f'''  tl.fromTo('#c-dist-p{j}',{{opacity:0,scale:0.7,y:12}},{{opacity:1,scale:1,y:0,duration:0.42,ease:"back.out(2)"}},{js:.4f});''')
card_tl.append(f'''  tl.to('.card-host[data-card-id="c-dist"]',{{opacity:0,duration:0.28,ease:"power2.in"}},{q(e-0.10):.4f});
  tl.set('.card-host[data-card-id="c-dist"]',{{visibility:"hidden"}},{q(e):.4f});''')

# ---------------- KEN BURNS on #video-wrap (sequential scale, no overlap) ----------------
kb=[]
kb.append(f'  tl.set("#video-wrap",{{transformOrigin:"50% 42%",scale:1.03}},0);')
def kbto(scale,at,dur,ease="power2.out"):
    kb.append(f'  tl.to("#video-wrap",{{scale:{scale},duration:{dur},ease:"{ease}"}},{q(at):.4f});')
kbto(1.055,0.0,2.90,"none")       # slow hook push
kbto(1.02,2.96,0.45)              # reset on reason1
kbto(1.05,3.5,4.0,"none")         # slow drift through reason1
kbto(1.02,13.5,0.45)             # reset reason2
kbto(1.045,14.0,5.0,"none")
kbto(1.03,19.5,0.5)              # settle for checklist
kbto(1.05,25.2,3.0,"none")
kbto(1.02,30.9,0.45)             # reset reason3
kbto(1.06,31.5,4.0,"none")
kbto(1.04,40.0,3.4,"none")

# ---------------- ASSEMBLE ----------------
brandcss=open("public/fonts/brandfonts.css").read()
TL="\n".join(kb+["\n  // subtitles"]+sub_tl+["\n  // cards"]+card_tl)

doc=f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<style>
{brandcss}
:root{{ --bg:#16161A; --graphite:#16161A; --text:#F5F2EC; --accent:#E11D2A; }}
*{{box-sizing:border-box;}}
html,body{{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#000;
  font-family:'Manrope','Unbounded',ui-sans-serif,system-ui,sans-serif;}}
#stage{{position:relative;width:100%;height:100%;overflow:hidden;background:#000;}}
.video-wrapper{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;}}
.video-wrapper video{{width:100%;height:100%;object-fit:cover;}}
.card-host{{position:absolute;pointer-events:none;overflow:visible;}}
.card-host .root{{width:100%;height:100%;}}

/* ---- subtitles ---- */
.card-host.sub{{display:flex;align-items:center;justify-content:center;text-align:center;}}
.subline{{font-family:'Unbounded','Manrope',sans-serif;font-weight:800;line-height:1.02;
  white-space:nowrap;letter-spacing:.2px;}}
.subline .w{{color:var(--text);
  -webkit-text-stroke:2px #0a0a0b; paint-order:stroke fill;
  text-shadow:0 3px 12px rgba(0,0,0,.55),0 0 2px rgba(0,0,0,.9);}}
.subline .acc{{color:var(--accent);font-style:italic;
  -webkit-text-stroke:1.5px #2a0406; paint-order:stroke fill;
  text-shadow:0 0 20px rgba(225,29,42,.55),0 3px 10px rgba(0,0,0,.6);}}

/* ---- kicker ---- */
.pill-k{{display:flex;align-items:center;gap:12px;justify-content:center;
  background:rgba(22,22,26,.82);border:1px solid rgba(245,242,236,.14);border-radius:999px;
  padding:0 26px;height:100%;backdrop-filter:blur(4px);}}
.pill-k .dot{{width:12px;height:12px;background:var(--accent);border-radius:2px;transform:rotate(45deg);box-shadow:0 0 12px rgba(225,29,42,.7);}}
.pill-k .kt{{font-family:'Manrope';font-weight:700;color:var(--text);font-size:26px;letter-spacing:3px;}}

/* ---- chapter ---- */
.chap{{display:flex;align-items:center;gap:16px;justify-content:center;
  background:rgba(22,22,26,.85);border-radius:18px;padding:0 30px;height:100%;
  border:1px solid rgba(245,242,236,.12);box-shadow:0 10px 30px rgba(0,0,0,.4);}}
.chap .cn{{font-family:'Unbounded';font-weight:800;font-size:56px;color:var(--accent);
  text-shadow:0 0 18px rgba(225,29,42,.5);line-height:1;}}
.chap .cl{{font-family:'Manrope';font-weight:700;font-size:30px;color:var(--text);letter-spacing:2px;}}

/* ---- stat callout ---- */
.statc{{background:linear-gradient(180deg,rgba(22,22,26,.92),rgba(22,22,26,.86));
  border-radius:26px;border:1px solid rgba(245,242,236,.10);
  box-shadow:0 18px 50px rgba(0,0,0,.5);padding:26px 34px;position:relative;
  display:flex;flex-direction:column;justify-content:center;overflow:hidden;}}
.statc:before{{content:"";position:absolute;left:0;top:0;bottom:0;width:10px;background:var(--accent);box-shadow:0 0 20px rgba(225,29,42,.6);}}
.statc .sk{{font-family:'Manrope';font-weight:700;color:#cfc9bd;font-size:30px;letter-spacing:3px;margin-left:8px;}}
.statc .sv{{font-family:'Unbounded';font-weight:800;color:var(--accent);line-height:1;margin-top:6px;margin-left:6px;
  text-shadow:0 0 26px rgba(225,29,42,.45);display:flex;align-items:baseline;}}
.statc .sv .pre{{font-size:96px;}} .statc .sv .num{{font-size:150px;font-family:'JetBrains Mono';font-weight:700;}}
.statc .sv .suf{{font-size:96px;margin-left:4px;}}
.statc .bar{{height:8px;margin-top:14px;margin-left:6px;background:var(--accent);border-radius:4px;transform-origin:left center;box-shadow:0 0 14px rgba(225,29,42,.6);}}

/* ---- money ---- */
.money{{background:rgba(22,22,26,.92);border-radius:26px;border:1px solid rgba(245,242,236,.10);
  box-shadow:0 18px 50px rgba(0,0,0,.5);padding:28px 34px;display:flex;flex-direction:column;justify-content:center;}}
.money .mk{{font-family:'Manrope';font-weight:700;color:#cfc9bd;font-size:28px;letter-spacing:3px;}}
.money .mrow{{display:flex;align-items:center;justify-content:center;gap:20px;margin-top:14px;font-family:'JetBrains Mono';font-weight:700;white-space:nowrap;}}
.money .was{{color:#8b8578;font-size:58px;text-decoration:line-through;text-decoration-color:rgba(225,29,42,.7);white-space:nowrap;}}
.money .arr{{color:var(--text);font-size:52px;}}
.money .now{{color:var(--accent);font-size:72px;text-shadow:0 0 24px rgba(225,29,42,.5);white-space:nowrap;}}

/* ---- checklist ---- */
.feat{{display:flex;flex-direction:column;gap:18px;justify-content:center;}}
.frow{{display:flex;align-items:center;gap:20px;background:rgba(22,22,26,.80);border-radius:16px;
  padding:16px 24px;border:1px solid rgba(245,242,236,.10);box-shadow:0 8px 24px rgba(0,0,0,.35);}}
.frow .chk{{width:52px;height:52px;flex:0 0 52px;display:flex;align-items:center;justify-content:center;
  background:var(--accent);color:#fff;border-radius:12px;font-size:34px;font-weight:800;box-shadow:0 0 16px rgba(225,29,42,.5);}}
.frow .ft{{font-family:'Manrope';font-weight:700;color:var(--text);font-size:40px;letter-spacing:.5px;}}

/* ---- districts ---- */
.dist{{display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:center;}}
.dpill{{font-family:'Manrope';font-weight:700;font-size:38px;color:var(--text);letter-spacing:1px;
  background:rgba(22,22,26,.86);border:1px solid var(--accent);border-radius:999px;padding:14px 30px;
  box-shadow:0 0 20px rgba(225,29,42,.25),0 10px 26px rgba(0,0,0,.4);}}
</style>
</head>
<body>
<div id="stage" data-composition-id="dubai-remont" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
  <div class="video-wrapper" id="video-wrap">
    <video id="bg-video" src="input-video.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="1"></video>
  </div>
  <audio id="source-audio" src="input-video.mp4" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  <audio id="bgm" src="media/bgm.mp3" data-start="0" data-duration="{DUR}" data-track-index="11" data-volume="0.12"></audio>

{chr(10).join(card_hosts)}

{chr(10).join(sub_hosts)}

  <script src="vendor/gsap.min.js"></script>
  <script>
  (function(){{
    const tl=window.gsap.timeline({{paused:true}});
{TL}
    window.__timelines=window.__timelines||{{}};
    window.__timelines["dubai-remont"]=tl;
  }})();
  </script>
</div>
</body>
</html>'''

os.makedirs("public",exist_ok=True)
open("public/index.html","w").write(doc)
# storyboard for the record
json.dump({"schemaVersion":3,"composition":{"fps":FPS,"width":W,"height":H,"durationSeconds":DUR,"layout":"portrait","themeId":"custom-brand","seed":7},
 "videoTrack":{"sourcePath":"input-video.mp4","startSec":0,"endSec":DUR},
 "subtitles":{"enabled":True,"count":len(SUBS)},
 "cards":["c-kicker","c-ch1","c-stat1","c-money","c-ch2","c-feat","c-ch3","c-stat2","c-dist"]},
 open("storyboard.json","w"),ensure_ascii=False,indent=1)
print(f"index.html written: {os.path.getsize('public/index.html')} bytes")
print(f"subtitles: {len(sub_hosts)} | cards: {len(card_hosts)} | dur {DUR}s")
