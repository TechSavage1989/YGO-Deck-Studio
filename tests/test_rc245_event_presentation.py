import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
js_source=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
css=(root/'web/duel-core.css').read_text(encoding='utf-8')
assert "duelcore.1-rc259" in js_source
assert '.duel-event-callout' in css and '.duel-card-counter-badge' in css
js=js_source.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;window.__formatPosition=formatPosition;'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page()
    page.set_content('<!doctype html><html><head><style>'+css+'</style></head><body><div id="board" style="position:relative;width:900px;height:600px"></div></body></html>')
    page.add_script_tag(content=js)
    result=page.evaluate('''async()=>{
      const proto=window.IntegratedDuelController.prototype;
      const T={TOSS_COIN:130,TOSS_DICE:131,ADD_COUNTER:101,REMOVE_COUNTER:102,EQUIP:93,SWAP:55,MISSED_EFFECT:120,FIELD_DISABLED:56,HAND_RES:133,BATTLE:111,SHUFFLE_SET_CARD:36};
      const L={DECK:1,HAND:2,MZONE:4,SZONE:8,GRAVE:16,REMOVED:32,EXTRA:64};
      const P={FACEUP_ATTACK:1,FACEDOWN_ATTACK:2,FACEUP_DEFENSE:4,FACEDOWN_DEFENSE:8,FACEUP:5,FACEDOWN:10,ATTACK:3,DEFENSE:12};
      const names={1:'Breaker the Magical Warrior',2:'Axe of Despair',3:'Vorse Raider',4:'Mystical Elf',5:'Peten the Dark Clown',6:'Salamangreat Sunlight Wolf'};
      const emptyPlayer=()=>({mzone:Array(7).fill(null),szone:Array(8).fill(null),hand:[],deck:[],grave:[],removed:[],extra:[]});
      const c=Object.create(proto),logs=[],sounds=[];
      Object.assign(c,{mod:{OcgMessageType:T,OcgLocation:L,OcgPosition:P},field:{players:[emptyPlayer(),emptyPlayer()],chain:[]},logicalToCorePlayer:[1,0],coreToLogicalPlayer:[1,0],boardWrap:document.getElementById('board'),duelAnimationsEnabled:true,opponentCardsVisible:false,turn:2,chainEffectCodes:new Map(),chainEffectSources:new Map(),chainHistory:new Map()});
      c.log=(text,details)=>logs.push({text,type:details?.type,outcome:details?.outcome});c.playSound=k=>sounds.push(k);c.cardName=code=>names[code]||'Card '+code;c.currentResolutionCause=()=>null;c.isReplaySeekReconstruction=()=>false;c.actionPresentationScale=()=>0.05;
      c.getCardById=code=>code===6?{type:'Link Effect Monster'}:{type:'Effect Monster'};
      c.field.players[0].mzone[1]={code:1,controller:0,location:L.MZONE,sequence:1,position:P.FACEUP_ATTACK};
      c.field.players[0].mzone[2]={code:3,controller:0,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK};
      c.field.players[0].szone[0]={code:2,controller:0,location:L.SZONE,sequence:0,position:P.FACEUP_ATTACK};
      c.field.players[1].mzone[0]={code:4,controller:1,location:L.MZONE,sequence:0,position:P.FACEDOWN_DEFENSE};
      const handled={};
      handled.coin1=c.consumePresentationEvent({type:T.TOSS_COIN,player:0,results:[true]});
      handled.coin3=c.consumePresentationEvent({type:T.TOSS_COIN,player:1,results:[true,false,true]});
      handled.dice=c.consumePresentationEvent({type:T.TOSS_DICE,player:0,results:[4]});
      handled.add=c.consumePresentationEvent({type:T.ADD_COUNTER,controller:0,location:L.MZONE,sequence:1,count:1,counter_type:1});
      handled.remove=c.consumePresentationEvent({type:T.REMOVE_COUNTER,controller:0,location:L.MZONE,sequence:1,count:2,counter_type:1});
      handled.equip=c.consumePresentationEvent({type:T.EQUIP,card:{controller:0,location:L.SZONE,sequence:0,position:P.FACEUP_ATTACK},target:{controller:0,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK}});
      handled.missed=c.consumePresentationEvent({type:T.MISSED_EFFECT,code:5,controller:0,location:L.GRAVE,sequence:0,position:P.FACEUP_ATTACK});
      handled.hidden=c.consumePresentationEvent({type:T.ADD_COUNTER,controller:1,location:L.MZONE,sequence:0,count:1});
      handled.rps=c.consumePresentationEvent({type:T.HAND_RES,results:[2,3]});
      handled.battle=c.consumePresentationEvent({type:T.BATTLE,card:{controller:0,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK,attack:1900,defense:1200,destroyed:false},target:{controller:1,location:L.MZONE,sequence:0,position:P.FACEDOWN_DEFENSE,attack:800,defense:2000,destroyed:false}});
      const before=logs.length;handled.direct=c.consumePresentationEvent({type:T.BATTLE,card:{controller:0,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK,attack:1900,defense:1200,destroyed:false},target:{controller:0,location:0,sequence:0,position:0,attack:0,defense:0,destroyed:false}});handled.directLogged=logs.length-before;
      handled.zones=c.consumePresentationEvent({type:T.FIELD_DISABLED,field_mask:0b101});
      handled.unknown=c.consumePresentationEvent({type:9999});
      const calloutNow=document.querySelector('.duel-event-callout')?.textContent||'';
      await new Promise(r=>setTimeout(r,700));
      const calloutsAfter=document.querySelectorAll('.duel-event-callout').length;
      const fp=window.__formatPosition;
      const wording={grave:c.positionPhrase(5,L.GRAVE,' '),mzone:c.positionPhrase(P.FACEUP_ATTACK,L.MZONE,' '),set:c.positionPhrase(P.FACEDOWN_DEFENSE,L.MZONE,' '),szoneUp:c.positionPhrase(5,L.SZONE,' '),szoneDown:c.positionPhrase(10,L.SZONE,' '),hand:c.positionPhrase(10,L.HAND,' '),
        flipSpell:c.positionChangePhrase(5,L.SZONE),monster:c.positionChangePhrase(P.FACEUP_DEFENSE,L.MZONE),fp5:fp(c.mod,5),fp99:fp(c.mod,99)};
      const strip={link:c.effectTextWithoutMaterials(6,'2 FIRE Effect Monsters\\r\\nIf a monster is Special Summoned: You can add 1 FIRE monster.'),main:c.effectTextWithoutMaterials(1,'Line one\\nLine two'),single:c.effectTextWithoutMaterials(6,'Only one line.')};
      return{handled,logs,sounds,calloutNow,calloutsAfter,wording,strip};
    }''')
    browser.close()
print(result)
h=result['handled'];texts=[l['text'] for l in result['logs']];types=[l['type'] for l in result['logs']]
assert h['direct'] is True and h['directLogged']==0, h  # a direct attack has no second monster to compare
assert all(h[k] for k in ('coin1','coin3','dice','add','remove','equip','missed','hidden','rps','battle','zones')) and h['unknown'] is False, h
assert 'Player tosses a coin: Heads.' in texts and any('tosses 3 coins: Heads, Tails, Heads (2 Heads, 1 Tails)' in t for t in texts), texts
assert 'Player rolls a die: 4.' in texts, texts
assert 'Breaker the Magical Warrior gains 1 counter.' in texts and 'Breaker the Magical Warrior loses 2 counters.' in texts, texts
assert 'Axe of Despair is equipped to Vorse Raider.' in texts, texts
assert any(t.startswith("Peten the Dark Clown's optional") and 'missed its timing' in t for t in texts), texts
# A face-down opponent monster is never named.
assert 'A card gains 1 counter.' in texts and not any('Mystical Elf gains' in t for t in texts), texts
assert any('vs a card (2000 DEF) - neither is destroyed' in t for t in texts), texts
# Rock-Paper-Scissors results are indexed by core player and must be mapped.
assert 'Rock-Paper-Scissors: Player shows Paper, Practice Dummy shows Rock.' in texts, texts
assert '2 zones are currently unusable.' in texts, texts
for needed in ('coin','dice','counter','equip','missed-timing','battle-calc','rps','zone-disabled'): assert needed in types,(needed,types)
assert result['sounds'][:3]==['coin','coin','dice'] and 'missed' in result['sounds'], result['sounds']
assert 'COIN TOSS' in result['calloutNow'] and result['calloutsAfter']==0, result
w=result['wording']
assert w['grave']=='' and w['hand']=='' and w['mzone']==' in Attack Position' and w['set']==' in Face-down Defense Position' and w['szoneUp']==' face-up' and w['szoneDown']==' face-down', w
assert w['flipSpell']=='is turned face-up' and w['monster']=='changes to Defense Position' and w['fp5']=='Face-up' and w['fp99']=='', w
s=result['strip']
assert s['link'].startswith('If a monster is Special Summoned') and s['main']=='Line one\nLine two' and s['single']=='Only one line.', s
print('rc245 event presentation regression passed')
