"""rc252: canvas particle effects for card actions.

Every named effect must start, draw visible pixels on the canvas, and clean the canvas up when it ends.
Effects must not run with animations off, and card moves must map to the right effect.
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
core=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
css=(root/'web/duel-core.css').read_text(encoding='utf-8')
assert "duelcore.1-rc263" in core
assert '.duel-fx-canvas' in css
js=core.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'
NAMES=['summon','special','fusion','synchro','xyz','link','ritual','activate','negated','disabled','destroyed','togy','banished','tohand','todeck','targeted','statup','statdown','unaffected','impact']

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':800,'height':600})
    page.set_content('<!doctype html><html><head><style>'+css+'html,body{background:#000!important}</style></head><body></body></html>')
    page.add_script_tag(content=js)
    result=page.evaluate('''(names)=>{
      let cb=null,now=1000;window.requestAnimationFrame=f=>{cb=f;return 1};
      const step=()=>{now+=33;const f=cb;cb=null;if(f)f(now);};
      const L={DECK:1,HAND:2,MZONE:4,SZONE:8,GRAVE:16,REMOVED:32,EXTRA:64};
      const c=Object.create(window.IntegratedDuelController.prototype);Object.assign(c,{duelAnimationsEnabled:true,battleEffectIntensity:'standard',mod:{OcgLocation:L}});c.isReplaySeekReconstruction=()=>false;c.traceSession=()=>{};
      const out={};
      for(const name of names){
        const started=c.playFx(name,400,300,{w:60,h:86,tx:700,ty:500});let lit=0,frames=0;
        for(let i=0;i<120&&c.fxState;i++){step();frames++;const s=c.fxState;if(s&&i%4===2){const d=s.ctx.getImageData(0,0,s.canvas.width,s.canvas.height).data;let n=0;for(let k=3;k<d.length;k+=16)if(d[k]>24)n++;if(n>lit)lit=n;}}
        out[name]={started,lit,frames,cleaned:!c.fxState&&!document.querySelector('.duel-fx-canvas')};
      }
      const unknown=c.playFx('nope',400,300);
      c.duelAnimationsEnabled=false;const off=c.playFx('summon',400,300);c.duelAnimationsEnabled=true;
      const mv=(from,to,kind='move')=>c.fxForMove({kind,from:{location:from},to:{location:to}});
      const moves={gy:mv(L.MZONE,L.GRAVE),ban:mv(L.GRAVE,L.REMOVED),hand:mv(L.MZONE,L.HAND),search:mv(L.DECK,L.HAND),deck:mv(L.HAND,L.DECK),extra:mv(L.MZONE,L.EXTRA),field:mv(L.HAND,L.MZONE),draw:mv(L.DECK,L.HAND,'draw-flight')};
      return{out,unknown,off,moves,leftover:document.querySelectorAll('.duel-fx-canvas').length};
    }''',NAMES)
    browser.close()

for name in NAMES:
    r=result['out'][name]
    assert r['started'] is True,(name,r)
    assert r['lit']>=40,(name,r)          # visibly drawn, not a stray pixel
    assert 8<=r['frames']<=75,(name,r)    # between a quarter second and two and a half seconds
    assert r['cleaned'],(name,r)
assert result['unknown'] is False and result['off'] is False
assert result['moves']=={'gy':'togy','ban':'banished','hand':'tohand','search':'','deck':'todeck','extra':'todeck','field':'','draw':''},result['moves']
assert result['leftover']==0
print('rc252 particle effects: '+', '.join(f"{n} {result['out'][n]['frames']}f" for n in NAMES))
