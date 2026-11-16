"""rc253: the Deck shuffle plays a recording of real cards, even when it is the first sound of the duel."""
import os,re,json
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
core=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
app=(root/'web/js/app.js').read_text(encoding='utf-8')
assert "duelcore.1-rc257" in core
table=json.loads(re.search(r'globalThis\.YGO_DUEL_SFX=(\{.*?\});',app).group(1))
assert 'shuffle' in table
js=core.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    page=browser.new_page();page.set_content('<!doctype html><html><body></body></html>')
    page.add_script_tag(content='globalThis.YGO_DUEL_SFX='+json.dumps(table)+';');page.add_script_tag(content=js)
    result=page.evaluate('''async()=>{
      const make=()=>{const c=Object.create(window.IntegratedDuelController.prototype);Object.assign(c,{soundEnabled:true});c.isReplaySeekReconstruction=()=>false;c.isSoundEffectEnabled=()=>true;c.effectiveSoundVolume=()=>1;return c;};
      const run=async(c)=>{const ctx=new AudioContext();c.ensureAudio=()=>ctx;const played=[];const cbs=ctx.createBufferSource.bind(ctx);ctx.createBufferSource=()=>{const s=cbs();const start=s.start.bind(s);s.start=(...a)=>{played.push(s.buffer?.duration||0);return start(...a)};return s};
        let legacy=0;const old=c.playLegacyDeckShuffleSound.bind(c);c.playLegacyDeckShuffleSound=x=>{legacy++;return old(x)};
        const returned=c.playDeckShuffleSound();await new Promise(r=>setTimeout(r,1500));return{returned,played,legacy};};
      const first=await run(make());                       // first sound of the duel: clip not decoded yet
      const broken=make();const saved=globalThis.YGO_DUEL_SFX;globalThis.YGO_DUEL_SFX={...saved,shuffle:'AAAA'};const fallback=await run(broken);globalThis.YGO_DUEL_SFX=saved;
      const c=make();c.soundSampleMix('shuffle');return{first,fallback,mix:c.soundSampleMix('shuffle')};
    }''')
    browser.close()

first=result['first']
assert first['returned'] is True and first['legacy']==0,first
assert len(first['played'])==1 and 0.8<=first['played'][0]<=1.6,first
assert result['fallback']['legacy']==1,result['fallback']   # undecodable clip falls back to the older one
assert result['mix'][1]<0.1
print('rc253 real shuffle recording plays first time; fallback intact')
