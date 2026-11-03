import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
js_source=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
assert "duelcore.1-rc243" in js_source
# Field refresh must not request QUERY_TYPE: the ocgcore-wasm reader has no branch for it and loses every later field.
assert 'const flags = Q.CODE|Q.POSITION|Q.LEVEL|Q.RANK|Q.ATTRIBUTE|Q.ATTACK|Q.DEFENSE|Q.OWNER|Q.IS_PUBLIC|Q.LINK|Q.OVERLAY_CARD;' in js_source
assert 'Q.TYPE' not in js_source
assert "'triggering_controller'" in js_source
js=js_source.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'
html='<!doctype html><html><head></head><body><div id="root"></div></body></html>'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page()
    page.set_content(html)
    page.add_script_tag(content=js)
    result=page.evaluate('''()=>{
      const proto=window.IntegratedDuelController.prototype;
      const T={CHAINING:60,SELECT_CHAIN:16,SELECT_IDLECMD:11,SELECT_CARD:15,RETRY:1};
      const R={SELECT_IDLECMD:3,SELECT_CHAIN:8,SELECT_CARD:5};
      const I={SELECT_SUMMON:0,SELECT_SPECIAL_SUMMON:1,SELECT_POS_CHANGE:2,SELECT_MONSTER_SET:3,SELECT_SPELL_SET:4,SELECT_ACTIVATE:5,TO_BP:6,TO_EP:7};
      const L={DECK:1,HAND:2,MZONE:4,SZONE:8,GRAVE:16,REMOVED:32,EXTRA:64};
      const P={FACEUP_ATTACK:1,FACEDOWN_ATTACK:2,FACEUP_DEFENSE:4,FACEDOWN_DEFENSE:8,FACEUP:5,FACEDOWN:10};
      const H={SUMMON:0x40,SPSUMMON:0x80,FLIPSUMMON:0x100,ATTACK:0x1000,DAMAGE_STEP:0x2000,DAMAGE_CAL:0x4000};
      const DARK_HOLE=53129443,MST=5318639,ASH=14558127,SAKURETSU=56120475,TRAP_HOLE=4206964,SAGE=8240199,SPIRIT=59882179,BUG=13039848,ELF=15025844,BEWD=89631139,VORSE=91949988,CRY=1819262;
      const cards={
        [DARK_HOLE]:{name:'Dark Hole',type:'Normal Spell',desc:'Destroy all monsters on the field.'},
        [MST]:{name:'Mystical Space Typhoon',type:'Quick-Play Spell',desc:'Target 1 Spell/Trap on the field; destroy that target.'},
        [ASH]:{name:'Ash Blossom & Joyous Spring',type:'Tuner Effect Monster',atk:0,def:1800,desc:'When a card or effect is activated that includes any of these effects (Quick Effect): You can discard this card; negate that effect.'},
        [SAKURETSU]:{name:'Sakuretsu Armor',type:'Normal Trap',desc:"When an opponent's monster declares an attack: Target the attacking monster; destroy that target."},
        [TRAP_HOLE]:{name:'Trap Hole',type:'Normal Trap',desc:'When your opponent Normal or Flip Summons a monster with 1000 or more ATK: Target that monster; destroy that target.'},
        [SAGE]:{name:'Sage with Eyes of Blue',type:'Tuner Effect Monster',atk:0,def:1500,desc:'When this card is Normal Summoned: You can add 1 Level 1 LIGHT Tuner from your Deck to your hand.'},
        [SPIRIT]:{name:'Blue-Eyes Spirit Dragon',type:'Synchro Effect Monster',atk:2500,def:3000,desc:'Once per turn, during either player\\'s turn: You can Tribute this card; Special Summon 1 Level 8 or lower Dragon Synchro Monster from your Extra Deck in Defense Position.'},
        [BUG]:{name:'Man-Eater Bug',type:'Flip Effect Monster',atk:450,def:600,desc:'FLIP: Target 1 monster on the field; destroy that target.'},
        [ELF]:{name:'Mystical Elf',type:'Normal Monster',atk:800,def:2000,desc:'A delicate elf.'},
        [BEWD]:{name:'Blue-Eyes White Dragon',type:'Normal Monster',atk:3000,def:2500,desc:'This legendary dragon is a powerful engine of destruction.'},
        [VORSE]:{name:'Vorse Raider',type:'Normal Monster',atk:1900,def:1200,desc:'This wicked Beast-Warrior does every horrible thing imaginable.'},
        [CRY]:{name:"Silver's Cry",type:'Quick-Play Spell',desc:'Target 1 Dragon Normal Monster in your GY; Special Summon that target.'},
      };
      const db={[ASH]:{attack:0,defense:1800,type:0x1021},[SAGE]:{attack:0,defense:1500,type:0x1021},[SPIRIT]:{attack:2500,defense:3000,type:0x2021},[BUG]:{attack:450,defense:600,type:0x200021},[ELF]:{attack:800,defense:2000,type:0x11},[BEWD]:{attack:3000,defense:2500,type:0x11},[VORSE]:{attack:1900,defense:1200,type:0x11},[DARK_HOLE]:{type:0x2},[MST]:{type:0x10002},[SAKURETSU]:{type:0x4},[TRAP_HOLE]:{type:0x4},[CRY]:{type:0x10002}};
      const emptyPlayer=()=>({mzone:Array(7).fill(null),szone:Array(8).fill(null),hand:[],deck:[],grave:[],removed:[],extra:[]});
      const make=()=>{
        const c=Object.create(proto);
        Object.assign(c,{mod:{OcgMessageType:T,OcgResponseType:R,SelectIdleCMDAction:I,OcgLocation:L,OcgPosition:P,OcgHintTiming:H},
          logicalToCorePlayer:[0,1],coreToLogicalPlayer:[0,1],field:{players:[emptyPlayer(),emptyPlayer()],chain:[]},lp:[8000,8000],
          chainHistory:new Map(),chainEffectSources:new Map(),chainEffectCodes:new Map(),pendingEffectSource:null,activeEffectDescription:'',pendingSpecialSummon:null,
          lastSummonContext:[null,null],lastAttackContext:null,turn:3,turnPlayer:1,duelStateRevision:20,resolvingChainLink:0,lastActivatedChainLink:0,
          dummyDifficulty:'expert',dummyPersonality:'auto',dummyStrategyProfile:null,dummyPlan:{turn:0,intents:[],recentCodes:[],nextTags:[],lastKind:'',lastCode:0},
          dummyActionHistory:new Map(),dummyPhaseActionCount:0,dummySafeModeThisTurn:false,projectIgnisSemantics:new Map()});
        c.getCardById=code=>cards[Number(code)]||null;c.cardData=code=>db[Number(code)]||null;
        c.effectLabel=item=>cards[Number(item?.code)]?.desc||'';c.descriptionText=()=> '';c.conciseEffectText=t=>String(t||'');
        c.projectIgnisEffectForActionItem=()=>null;c.inferPromptEffectText=()=>c.__effect||'';
        return c;
      };
      const out={};
      // 1. Core-to-logical mapping covers triggering_controller when the Dummy opened the duel.
      {const c=make();c.logicalToCorePlayer=[1,0];c.coreToLogicalPlayer=[1,0];const m=c.mapCoreMessage({type:T.CHAINING,controller:0,triggering_controller:0,code:DARK_HOLE});out.mappedController=m.controller;out.mappedTriggering=m.triggering_controller;}
      // 2. Board-aware activation assessment.
      {const c=make();c.field.players[1].mzone[2]={code:ELF,controller:1,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK};
       out.darkHoleEmptyOpponent=c.dummyActivationBoardAssessment({code:DARK_HOLE,controller:1,location:L.HAND,sequence:0});
       c.field.players[0].mzone[2]={code:VORSE,controller:0,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK};
       out.darkHoleWithTarget=c.dummyActivationBoardAssessment({code:DARK_HOLE,controller:1,location:L.HAND,sequence:0});
       c.field.players[1].szone[1]={code:SAKURETSU,controller:1,location:L.SZONE,sequence:1,position:P.FACEDOWN_ATTACK};
       out.mstOwnOnly=c.dummyActivationBoardAssessment({code:MST,controller:1,location:L.HAND,sequence:0});
       c.field.players[0].szone[1]={code:TRAP_HOLE,controller:0,location:L.SZONE,sequence:1,position:P.FACEDOWN_ATTACK};
       out.mstWithTarget=c.dummyActivationBoardAssessment({code:MST,controller:1,location:L.HAND,sequence:0});}
      // 3. Ash Blossom never negates the Dummy's own Chain Link but may answer the opponent's.
      {const c=make();const m={type:T.SELECT_CHAIN,player:1,forced:false,selects:[{code:ASH,controller:1,location:L.HAND,sequence:0}]};
       c.chainHistory.set(1,{code:SAGE,controller:1,chainLink:1,description:'add 1 Level 1 LIGHT Tuner from your Deck to your hand',respondsToController:0});
       out.ashOwnLink=c.dummyChainCandidateAssessment(m.selects[0],m);out.ashOwnLinkPass=c.dummyShouldPassChain(m);
       c.chainHistory.set(1,{code:CRY,controller:0,chainLink:1,description:'Add 1 Level 8 Dragon monster from your Deck to your hand, then Special Summon 1 Dragon monster from your hand.',respondsToController:0});
       out.ashOpponentLink=c.dummyChainCandidateAssessment(m.selects[0],m);out.ashOpponentLinkPass=c.dummyShouldPassChain(m);}
      // 4. Trigger detection distinguishes a card's own trigger from an event-activated Trap.
      {const c=make();out.sageTrigger=c.dummyChainCandidateIsTrigger({code:SAGE,controller:1,location:L.MZONE,sequence:0});out.sakuretsuTrigger=c.dummyChainCandidateIsTrigger({code:SAKURETSU,controller:1,location:L.SZONE,sequence:0});out.trapHoleTrigger=c.dummyChainCandidateIsTrigger({code:TRAP_HOLE,controller:1,location:L.SZONE,sequence:0});}
      // 5. Chain windows: hold quick effects on the Dummy's own quiet turn; answer opponent attacks and summons.
      {const c=make();const spirit={code:SPIRIT,controller:1,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK};c.field.players[1].mzone[2]=spirit;
       out.ownTurnQuiet=c.dummyShouldPassChain({type:T.SELECT_CHAIN,player:1,forced:false,hint_timing:0,selects:[spirit]});
       out.ownTurnTrigger=c.dummyShouldPassChain({type:T.SELECT_CHAIN,player:1,forced:false,hint_timing:0,selects:[{code:SAGE,controller:1,location:L.MZONE,sequence:0}]});
       const d=make();d.turnPlayer=0;d.field.players[0].mzone[0]={code:VORSE,controller:0,location:L.MZONE,sequence:0,position:P.FACEUP_ATTACK};
       d.lastAttackContext={attackerCode:VORSE,attackerController:0,direct:true,targetCode:0,expectedDamage:1900,turn:3};
       out.attackThreat=d.dummyChainWindowThreat({hint_timing:H.ATTACK});
       out.attackWindow=d.dummyShouldPassChain({type:T.SELECT_CHAIN,player:1,forced:false,hint_timing:H.ATTACK,selects:[{code:SAKURETSU,controller:1,location:L.SZONE,sequence:1}]});
       const e=make();e.turnPlayer=0;e.field.players[0].mzone[0]={code:VORSE,controller:0,location:L.MZONE,sequence:0,position:P.FACEUP_ATTACK};
       e.lastSummonContext[0]={code:VORSE,controller:0,kind:'normal',location:L.MZONE,sequence:0,turn:3,revision:18};
       out.summonThreat=e.dummyChainWindowThreat({hint_timing:H.SUMMON});
       out.summonWindow=e.dummyShouldPassChain({type:T.SELECT_CHAIN,player:1,forced:false,hint_timing:H.SUMMON,selects:[{code:TRAP_HOLE,controller:1,location:L.SZONE,sequence:1}]});
       const f=make();f.turnPlayer=0;out.opponentQuiet=f.dummyShouldPassChain({type:T.SELECT_CHAIN,player:1,forced:false,hint_timing:0,selects:[{code:MST,controller:1,location:L.SZONE,sequence:1}]});}
      // 6. Selection intent: shuffling an own card as part of a cost picks the least valuable target.
      {const c=make();c.__effect='Target 1 "Salamangreat" monster in your GY; shuffle that target into the Deck, and if you do, Special Summon this card.';
       const own=[{code:BEWD,controller:1,location:L.GRAVE,sequence:0},{code:ELF,controller:1,location:L.GRAVE,sequence:1}];
       out.costIntent=c.dummySelectionIntent({type:T.SELECT_CARD,selects:own});
       const ranked=c.dummyRankedSelectionCombos({type:T.SELECT_CARD,selects:own},1,1);out.costPick=ranked[0].indices;
       c.__effect='Target 1 Dragon Normal Monster in your GY; Special Summon that target.';out.summonIntent=c.dummySelectionIntent({type:T.SELECT_CARD,selects:own});
       out.summonPick=c.dummyRankedSelectionCombos({type:T.SELECT_CARD,selects:own},1,1)[0].indices;}
      // 7. Idle command: walls and FLIP monsters are Set, self-harming activations are withheld.
      {const c=make();const elf={code:ELF,controller:1,location:L.HAND,sequence:0},bug={code:BUG,controller:1,location:L.HAND,sequence:1},bewd={code:VORSE,controller:1,location:L.HAND,sequence:2};
       const first=c.dummyIdleChoices({type:T.SELECT_IDLECMD,player:1,summons:[elf],monster_sets:[elf],special_summons:[],pos_changes:[],spell_sets:[],activates:[],to_bp:true,to_ep:true})[0];out.elfChoice=first.action;
       const bugFirst=c.dummyIdleChoices({type:T.SELECT_IDLECMD,player:1,summons:[bug],monster_sets:[bug],special_summons:[],pos_changes:[],spell_sets:[],activates:[],to_bp:true,to_ep:true})[0];out.bugChoice=bugFirst.action;
       const beat=c.dummyIdleChoices({type:T.SELECT_IDLECMD,player:1,summons:[bewd],monster_sets:[bewd],special_summons:[],pos_changes:[],spell_sets:[],activates:[],to_bp:true,to_ep:true})[0];out.beaterChoice=beat.action;
       c.field.players[1].mzone[2]={code:ELF,controller:1,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK};
       const hole={code:DARK_HOLE,controller:1,location:L.HAND,sequence:3};
       const withHole=c.dummyIdleChoices({type:T.SELECT_IDLECMD,player:1,summons:[],monster_sets:[],special_summons:[],pos_changes:[],spell_sets:[hole],activates:[hole],to_bp:true,to_ep:true});
       out.darkHoleActivateOffered=withHole.some(r=>r.action===I.SELECT_ACTIVATE);out.darkHoleSetOffered=withHole.some(r=>r.action===I.SELECT_SPELL_SET);
       const spirit={code:SPIRIT,controller:1,location:L.MZONE,sequence:3,position:P.FACEUP_ATTACK};c.field.players[1].mzone[3]=spirit;
       const withSpirit=c.dummyIdleChoices({type:T.SELECT_IDLECMD,player:1,summons:[],monster_sets:[],special_summons:[],pos_changes:[],spell_sets:[],activates:[spirit],to_bp:true,to_ep:true});
       out.spiritSelfTributeOffered=withSpirit.some(r=>r.action===I.SELECT_ACTIVATE);}
      return out;
    }''')
    browser.close()
print(result)
assert result['mappedController']==1 and result['mappedTriggering']==1, result
assert result['darkHoleEmptyOpponent']['blocked'] is True, result
assert result['darkHoleWithTarget']['blocked'] is False, result
assert result['mstOwnOnly']['blocked'] is True, result
assert result['mstWithTarget']['blocked'] is False, result
assert result['ashOwnLink']['blocked'] is True and result['ashOwnLinkPass'] is True, result
assert result['ashOpponentLink']['blocked'] is False and result['ashOpponentLinkPass'] is False, result
assert result['sageTrigger'] is True and result['sakuretsuTrigger'] is False and result['trapHoleTrigger'] is False, result
assert result['ownTurnQuiet'] is True and result['ownTurnTrigger'] is False, result
assert result['attackThreat']['event']=='attack' and result['attackWindow'] is False, result
assert result['summonThreat']['event']=='summon' and result['summonWindow'] is False, result
assert result['opponentQuiet'] is True, result
assert result['costIntent']=='cost' and result['costPick']==[1], result
assert result['summonIntent']=='summon' and result['summonPick']==[0], result
assert result['elfChoice']==3 and result['bugChoice']==3 and result['beaterChoice']==0, result
assert result['darkHoleActivateOffered'] is False and result['darkHoleSetOffered'] is True, result
assert result['spiritSelfTributeOffered'] is False, result
print('rc242 Practice Dummy decision regression passed')
