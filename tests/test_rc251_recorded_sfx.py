"""rc251: duel sounds are recorded clips (CC0 sources), embedded in app.js and decoded by duel-core.js.

Decodes every embedded clip in a real browser, checks each one is audible and short, that every sound
kind the duel plays has a clip, and that playSound plays the clip once decoded and the synthesized
recipe before that (or when no clip exists).
"""
import os,re,json
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
core=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
app=(root/'web/js/app.js').read_text(encoding='utf-8')
assert "duelcore.1-rc251" in core
match=re.search(r'globalThis\.YGO_DUEL_SFX=(\{.*?\});',app)
assert match,'app.js must define the recorded clip table'
table=json.loads(match.group(1))
long_match=re.search(r'const DUEL_SFX_LONG=(\{.*?\});',core)
assert long_match,'duel-core.js must define the long clip table'
long_table=json.loads(long_match.group(1))
assert not set(table)&set(long_table)
legal=(root/'docs/LEGAL_NOTICE.txt').read_text(encoding='utf-8')
for name in ('Kenney','rubberduck','artisticdude','CC0'): assert name in legal,name
js=core.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    page=browser.new_page()
    page.set_content('<!doctype html><html><body></body></html>')
    page.add_script_tag(content='globalThis.YGO_DUEL_SFX='+json.dumps(table)+';')
    page.add_script_tag(content=js)
    result=page.evaluate('''async()=>{
      const proto=window.IntegratedDuelController.prototype,c=Object.create(proto);
      Object.assign(c,{soundEnabled:true});c.isReplaySeekReconstruction=()=>false;c.isSoundEffectEnabled=()=>true;c.effectiveSoundVolume=()=>1;c.preloadDeckShuffleSound=()=>{};c.preloadBattleAttackSound=()=>{};c.deckShuffleSoundBuffer=1;c.battleAttackSoundBuffer=1;
      const ctx=new AudioContext();c.ensureAudio=()=>ctx;
      let sources=0,oscillators=0;const cbs=ctx.createBufferSource.bind(ctx),co=ctx.createOscillator.bind(ctx);
      ctx.createBufferSource=()=>{sources++;return cbs()};ctx.createOscillator=()=>{oscillators++;return co()};
      // Before decoding finishes the synthesized recipe plays.
      c.playSound('summon');const fallbackOsc=oscillators;
      for(let i=0;i<100&&Object.keys(c.soundSamples||{}).length<Object.keys(globalThis.YGO_DUEL_SFX).length;i++)await new Promise(r=>setTimeout(r,50));
      const clips={};for(const [kind,b] of Object.entries(c.soundSamples||{})){const d=b.getChannelData(0);let peak=0;for(let i=0;i<d.length;i++){const v=Math.abs(d[i]);if(v>peak)peak=v;}clips[kind]={seconds:b.duration,peak};}
      const kinds=Object.keys(c.soundRecipes()),viaClip=[];
      for(const kind of kinds){c.soundLastPlayed?.clear?.();const s=sources,o=oscillators;c.playSound(kind,1000);if(sources===s+1&&oscillators===o)viaClip.push(kind);}
      const attack={};for(const style of ['slash','dragon','arcane','fire','machine']){const s=sources,o=oscillators;attack[style]=c.playGeneratedBattleAttackSound(style)===true&&sources===s+1&&oscillators===o;}
      // A kind without a clip still plays its recipe.
      delete c.soundSamples.negated;c.soundLastPlayed.clear();const o2=oscillators;c.playSound('negated');const recipeAfterRemoval=oscillators>o2;
      // Per-kind mix: interface clicks sit well under summons.
      const levels={select:c.soundSampleMix('select')[0],fusion:c.soundSampleMix('fusion')[0]};
      return{fallbackOsc,clips,kinds,viaClip,attack,recipeAfterRemoval,levels};
    }''')
    browser.close()

assert result['fallbackOsc']>0,'recipe must play while clips are still decoding'
table={**table,**long_table}
assert set(result['clips'])==set(table),sorted(set(table)-set(result['clips']))
for kind,clip in result['clips'].items():
    assert 0.12<=clip['seconds']<=2.0,(kind,clip)
    assert clip['peak']>=0.25,(kind,clip)
assert set(result['kinds'])<=set(table),sorted(set(result['kinds'])-set(table))
assert sorted(result['viaClip'])==sorted(result['kinds']),sorted(set(result['kinds'])-set(result['viaClip']))
assert all(result['attack'].values()),result['attack']
assert result['recipeAfterRemoval']
assert result['levels']['select']<result['levels']['fusion']
total=sum(len(v) for v in table.values())
assert total<140_000,total
print(f"rc251 recorded sound effects: {len(table)} clips, {total} base64 bytes, all decoded and routed")
