import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
js_source=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
css=(root/'web/duel-core.css').read_text(encoding='utf-8')
assert "duelcore.1-rc264" in js_source
for cls in ('.duel-attack-lunge','.duel-attack-recoil','.duel-destroy-burst','.duel-destroy-tile','.duel-summon-ring','.duel-summon-pillar','.duel-activation-pulse','.duel-attack-slash','prefers-reduced-motion'): assert cls in css,cls
js=js_source.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page()
    page.set_content('<!doctype html><html><head><style>'+css+'</style></head><body><div id="board" style="position:relative;width:900px;height:600px"><div class="duel-card" data-player="0" data-location="mzone" data-sequence="2" style="position:absolute;left:400px;top:400px;width:60px;height:86px"></div><div class="duel-card" data-player="1" data-location="mzone" data-sequence="1" style="position:absolute;left:400px;top:100px;width:60px;height:86px"></div></div></body></html>')
    page.add_script_tag(content=js)
    result=page.evaluate('''async()=>{
      const proto=window.IntegratedDuelController.prototype;
      const nodes={osc:0,noise:0,gains:[]};
      const param=()=>({value:0,setValueAtTime(){},exponentialRampToValueAtTime(){}});
      const ctx={currentTime:0,sampleRate:8000,state:'running',destination:{},createGain(){const g={gain:param(),connect(){}};nodes.gains.push(g);return g},createOscillator(){nodes.osc++;return{type:'',frequency:param(),connect(){},start(){},stop(){}}},createBuffer(c,n){return{getChannelData:()=>new Float32Array(n)}},createBufferSource(){nodes.noise++;return{buffer:null,connect(){},start(){},stop(){}}},createBiquadFilter(){return{type:'',frequency:{value:0},Q:{value:0},connect(){}}}};
      const L={DECK:1,HAND:2,MZONE:4,SZONE:8,GRAVE:16,REMOVED:32,EXTRA:64};
      const c=Object.create(proto);Object.assign(c,{mod:{OcgLocation:L},boardWrap:document.getElementById('board'),soundEnabled:true,duelAnimationsEnabled:true,battleEffectIntensity:'normal',lastAttackContext:null});
      c.isReplaySeekReconstruction=()=>false;c.ensureAudio=()=>ctx;c.isSoundEffectEnabled=()=>true;c.effectiveSoundVolume=()=>1;c.preloadDeckShuffleSound=()=>{};c.preloadBattleAttackSound=()=>{};c.deckShuffleSoundBuffer=1;c.battleAttackSoundBuffer=1;
      c.getCardById=code=>({1:{type:'Fusion Effect Monster'},2:{type:'Synchro Monster'},3:{type:'XYZ Effect Monster'},4:{type:'Link Effect Monster'},5:{type:'Ritual Monster'},6:{type:'Effect Monster'}})[code]||null;
      c.rectForLocation=loc=>c.fieldCardNode(loc)?.getBoundingClientRect()||null;
      const recipes=c.soundRecipes(),kinds=Object.keys(recipes),silent=[],uncategorized=[];
      const categories=new Set(c.soundEffectDefinitions().map(d=>d[1]));
      for(const kind of kinds){const before=nodes.osc+nodes.noise;c.soundLastPlayed?.clear?.();c.playSound(kind,1000);if(nodes.osc+nodes.noise===before)silent.push(kind);if(!categories.has(c.soundCategoryForKind(kind)))uncategorized.push(kind);}
      // retrigger guard and damage scaling
      c.soundLastPlayed.clear();const b1=nodes.osc;c.playSound('destroyed');const firstCount=nodes.osc-b1;c.playSound('destroyed');const once=firstCount>0&&nodes.osc-b1===firstCount?1:0;
      const masterGain=amount=>{c.soundLastPlayed.clear();const start=nodes.gains.length;c.playSound('damage',amount);return nodes.gains[start].gain.value;};
      const small=masterGain(200),big=masterGain(4000);
      const summon=[c.summonPresentationKind({kind:'summon',code:1}),...[1,2,3,4,5,6,99].map(code=>c.summonPresentationKind({kind:'special',code})),c.summonPresentationKind({kind:'flip',code:1})];
      const outcomes=['negated','disabled','destroyed','banished','sent-to-gy','returned-to-hand','returned-to-deck','targeted','stat-increased','stat-decreased','released','material','discarded','summoned','resolved'].map(k=>c.outcomeSoundKind(k));
      c.playSummonRing({kind:'special',player:0,location:L.MZONE,sequence:2,code:4});const ring=document.querySelector('.duel-summon-ring')?.className||'',entrance={pillar:document.querySelectorAll('.duel-summon-pillar').length,flash:document.querySelectorAll('.duel-summon-flash').length,sparks:document.querySelectorAll('.duel-summon-spark').length,wash:document.querySelectorAll('.duel-summon-wash').length};c.playActivationPulse({player:0,location:L.MZONE,sequence:2});const pulses=document.querySelectorAll('.duel-activation-pulse').length;
      c.playAttackLunge({from:{controller:0,location:L.MZONE,sequence:2},target:{controller:1,location:L.MZONE,sequence:1}},0,-300);
      const attacker=c.fieldCardNode({controller:0,location:L.MZONE,sequence:2}),lunge=attacker.classList.contains('duel-attack-lunge'),lungeY=attacker.style.getPropertyValue('--lunge-y'),lungeX=attacker.style.getPropertyValue('--lunge-x');
      c.playBattleDestruction({controller:1,location:L.MZONE,sequence:1});
      await new Promise(r=>setTimeout(r,160));const burst=document.querySelectorAll('.duel-destroy-burst').length,shards=document.querySelectorAll('.duel-destroy-burst b').length,tiles=document.querySelectorAll('.duel-destroy-burst .duel-destroy-tile').length;
      await new Promise(r=>setTimeout(r,480));const recoil=c.fieldCardNode({controller:1,location:L.MZONE,sequence:1}).classList.contains('duel-attack-recoil');
      const slash=document.querySelectorAll('.duel-attack-slash').length;await new Promise(r=>setTimeout(r,1300));const leftover=document.querySelectorAll('.duel-destroy-burst,.duel-summon-ring,.duel-summon-pillar,.duel-summon-flash,.duel-summon-spark,.duel-activation-pulse,.duel-attack-slash,.duel-attack-lunge,.duel-attack-recoil,.duel-destroy-hidden').length;
      c.duelAnimationsEnabled=false;c.playBattleDestruction({controller:1,location:L.MZONE,sequence:1});await new Promise(r=>setTimeout(r,150));const disabledBurst=document.querySelectorAll('.duel-destroy-burst').length;
      return{entrance,pulses,tiles,slash,count:kinds.length,silent,uncategorized,once,small,big,summon,outcomes,ring,lunge,lungeX,lungeY,burst,shards,recoil,leftover,disabledBurst,hasOutcomeCategory:categories.has('outcome')};
    }''')
    browser.close()
print(result)
assert result['count']>=37 and result['silent']==[] and result['uncategorized']==[], result
assert result['hasOutcomeCategory'] and result['once']==1, result
assert result['big']>result['small']>0, result
assert result['summon']==['summon','fusion','synchro','xyz','link','ritual','special','special','flip'], result['summon']
assert result['outcomes']==['negated','negated','destroyed','banished','togy','returned','returned','targeted','statup','statdown','material','material','discarded','',''], result['outcomes']
assert 'type-link' in result['ring'], result
assert result['lunge'] and result['lungeX'] in ('0.0px','-0.0px') and result['lungeY'].startswith('-') and abs(float(result['lungeY'][:-2]))<=70, result
assert result['entrance']=={'pillar':1,'flash':1,'sparks':16,'wash':1} and result['pulses']==2 and result['tiles']==20 and result['slash']==1, result
assert result['burst']==1 and result['shards']==12 and result['recoil'] and result['leftover']==0 and result['disabledBurst']==0, result
print('rc247 battle effects and sound regression passed')
