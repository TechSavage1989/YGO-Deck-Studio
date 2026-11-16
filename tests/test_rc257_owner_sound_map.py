"""rc257: the owner's sound assignments. A Field Spell activation has its own sound kind; other
activations keep the normal one; since rc258 every summon type plays the Normal Summon clip."""
import os,re,json
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
core=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
app=(root/'web/js/app.js').read_text(encoding='utf-8')
assert "duelcore.1-rc259" in core
table={**json.loads(re.search(r'globalThis\.YGO_DUEL_SFX=(\{.*?\});',app).group(1)),**json.loads(re.search(r'const DUEL_SFX_LONG=(\{.*?\});',core).group(1))}
assert 'fieldspell' in table and 'summon' in table and 'activate' in table and 'xyz' not in table and 'special' not in table
js=core.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    page=browser.new_page();page.set_content('<!doctype html><html><body></body></html>')
    page.add_script_tag(content='globalThis.YGO_DUEL_SFX='+json.dumps(table)+';globalThis.__noLong=1;');page.add_script_tag(content=js)
    result=page.evaluate('''async()=>{
      const c=Object.create(window.IntegratedDuelController.prototype);Object.assign(c,{soundEnabled:true});c.isReplaySeekReconstruction=()=>false;c.isSoundEffectEnabled=()=>true;c.effectiveSoundVolume=()=>1;c.preloadDeckShuffleSound=()=>{};c.preloadBattleAttackSound=()=>{};c.deckShuffleSoundBuffer=1;c.battleAttackSoundBuffer=1;c.normalizeActionCode=x=>x;
      c.getCardById=code=>({1:{type:'Spell Card',race:'Field'},2:{type:'Spell Card',race:'Quick-Play'},3:{type:'Trap Card',race:'Normal'},4:{type:'Effect Monster',race:'Fiend'},5:{type:'Fusion Monster',race:'Dragon'}})[code]||null;
      const kinds={field:c.summonPresentationKind({kind:'activate',code:1}),quick:c.summonPresentationKind({kind:'activate',code:2}),trap:c.summonPresentationKind({kind:'activate',code:3}),monster:c.summonPresentationKind({kind:'activate',code:4}),fusion:c.summonPresentationKind({kind:'special',code:5}),normal:c.summonPresentationKind({kind:'summon',code:4})};
      const ctx=new AudioContext();c.ensureAudio=()=>ctx;c.playSound('select');
      for(let i=0;i<100&&Object.keys(c.soundSamples||{}).length<Object.keys(globalThis.YGO_DUEL_SFX).length;i++)await new Promise(r=>setTimeout(r,50));
      const played=[];const cbs=ctx.createBufferSource.bind(ctx);ctx.createBufferSource=()=>{const s=cbs();const st=s.start.bind(s);s.start=(...a)=>{played.push(s.buffer);return st(...a)};return s};
      const buf=k=>{c.soundLastPlayed.clear();played.length=0;c.playSound(k);return played[0]||null};
      const S=c.soundSamples;
      return{kinds,fieldUsesOwn:buf('fieldspell')===S.fieldspell,fusion:buf('fusion')===S.summon,synchro:buf('synchro')===S.summon,link:buf('link')===S.summon,ritual:buf('ritual')===S.summon,xyzOwn:buf('xyz')===S.summon&&buf('special')===S.summon&&buf('activate')===S.activate&&S.activate!==S.fieldspell,category:c.soundCategoryForKind('fieldspell')};
    }''')
    browser.close()

assert result['kinds']=={'field':'fieldspell','quick':'activate','trap':'activate','monster':'activate','fusion':'fusion','normal':'summon'},result['kinds']
for key in ('fieldUsesOwn','fusion','synchro','link','ritual','xyzOwn'): assert result[key] is True,(key,result)
assert result['category']=='activate'
# rc259: the summon sound is not gated on the showcase, so effect summons are not silent.
assert "if(item.kind!=='activate'||(shown&&!item.chainLink))this.playSound(this.summonPresentationKind(item));" in core
print('rc257 owner sound map: Field Spell activation, shared summon recording and Xyz confirmed')
