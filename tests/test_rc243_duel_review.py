import os
import subprocess
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
import patch_embedded_web as pw  # noqa: E402

js_source=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
assert "duelcore.1-rc243" in js_source

# 1. Embedded compaction: only literal-free lines change, meaning-bearing whitespace survives, output parses.
c=pw.compact_literal_free_js_line
assert c("  const a = b + c;")=="const a=b+c;"
assert c("if (x) { return y; } else { z(); }")=="if(x){return y;}else{z();}"
assert c("const d = a + +b - -c;")=="const d=a+ +b- -c;"
assert c("x = typeof (y) === 'string';")=="x = typeof (y) === 'string';"   # has a quote: untouched
assert c("const re = /a b/;")=="const re = /a b/;"                           # has a slash: untouched
assert c("const t = `a ${b} c`;")=="const t = `a ${b} c`;"                   # has a backtick: untouched
assert c("return new Foo(a, b);")=="return new Foo(a,b);"
for name,limit in (('web/js/duel-core.js',798551),('web/js/app.js',463846)):
    out=pw.replacement_bytes(root/name,name)
    assert len(out)<=limit,(name,len(out),limit)
    with tempfile.NamedTemporaryFile('wb',suffix='.js',delete=False) as handle:
        handle.write(out);path=handle.name
    try:
        subprocess.run(['node','--check',path],check=True)
    finally:
        os.unlink(path)

js=js_source.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page()
    page.set_content('<!doctype html><html><head></head><body><div id="root"></div></body></html>')
    page.add_script_tag(content=js)
    result=page.evaluate('''()=>{
      const proto=window.IntegratedDuelController.prototype;
      const T={SELECT_CHAIN:16,SELECT_IDLECMD:11,SELECT_EFFECTYN:12};
      const R={SELECT_IDLECMD:3,SELECT_CHAIN:8};
      const I={SELECT_SUMMON:0,SELECT_SPECIAL_SUMMON:1,SELECT_POS_CHANGE:2,SELECT_MONSTER_SET:3,SELECT_SPELL_SET:4,SELECT_ACTIVATE:5,TO_BP:6,TO_EP:7};
      const L={DECK:1,HAND:2,MZONE:4,SZONE:8,GRAVE:16,REMOVED:32,EXTRA:64};
      const P={FACEUP_ATTACK:1,FACEDOWN_ATTACK:2,FACEUP_DEFENSE:4,FACEDOWN_DEFENSE:8,FACEUP:5,FACEDOWN:10};
      const PH={END:0x200};
      const H={DRAW_PHASE:1,STANDBY_PHASE:2,MAIN_END:4,BATTLE_START:8,BATTLE_END:16,END_PHASE:32,SUMMON:64,SPSUMMON:128,ATTACK:4096,DAMAGE_STEP:8192,DAMAGE_CAL:16384,CHAIN_END:32768,TOGRAVE:8388608,BATTLED:134217728};
      const HONEST=37742478,BUG=13039848,ELF=15025844,VORSE=91949988,SKULL=70781052,PAY=1;
      const cards={[HONEST]:{name:'Honest',type:'Effect Monster',atk:1100,def:1900,desc:'During the Damage Step, if your LIGHT monster battles (Quick Effect): You can send this card from your hand to the GY; that monster gains ATK equal to the ATK of the monster it is battling.'},
        [BUG]:{name:'Man-Eater Bug',type:'Flip Effect Monster',atk:450,def:600,desc:'FLIP: Target 1 monster on the field; destroy that target.'},
        [ELF]:{name:'Mystical Elf',type:'Normal Monster',atk:800,def:2000,desc:'A delicate elf.'},
        [VORSE]:{name:'Vorse Raider',type:'Normal Monster',atk:1900,def:1200,desc:'A wicked Beast-Warrior.'},
        [SKULL]:{name:'Summoned Skull',type:'Normal Monster',atk:2500,def:1200,desc:'A fiend with dark powers.'}};
      const db={[HONEST]:{attack:1100,defense:1900,type:0x21},[BUG]:{attack:450,defense:600,type:0x200021},[ELF]:{attack:800,defense:2000,type:0x11},[VORSE]:{attack:1900,defense:1200,type:0x11},[SKULL]:{attack:2500,defense:1200,type:0x11}};
      const emptyPlayer=()=>({mzone:Array(7).fill(null),szone:Array(8).fill(null),hand:[],deck:[],grave:[],removed:[],extra:[]});
      const make=()=>{const c=Object.create(proto);Object.assign(c,{mod:{OcgMessageType:T,OcgResponseType:R,SelectIdleCMDAction:I,OcgLocation:L,OcgPosition:P,OcgPhase:PH,OcgHintTiming:H},
        logicalToCorePlayer:[0,1],coreToLogicalPlayer:[0,1],field:{players:[emptyPlayer(),emptyPlayer()],chain:[]},lp:[8000,8000],chainHistory:new Map(),chainEffectSources:new Map(),chainEffectCodes:new Map(),pendingEffectSource:null,activeEffectDescription:'',pendingSpecialSummon:null,
        lastSummonContext:[null,null],lastAttackContext:null,turn:3,turnPlayer:0,duelStateRevision:20,resolvingChainLink:0,lastActivatedChainLink:0,dummyDifficulty:'expert',dummyPersonality:'auto',dummyStrategyProfile:null,dummyPlan:{turn:0,intents:[],recentCodes:[],nextTags:[],lastKind:'',lastCode:0},dummyActionHistory:new Map(),dummyPhaseActionCount:0,dummySafeModeThisTurn:false,projectIgnisSemantics:new Map(),
        smartOptionalChainPromptsEnabled:true,suppressSelfNegatingHandTrapsEnabled:false,shiftChainOverrideHeld:false,meaningfulResponseWindow:false,phase:0x4});
        c.getCardById=code=>cards[Number(code)]||null;c.cardData=code=>db[Number(code)]||null;c.effectLabel=item=>cards[Number(item?.code)]?.desc||'';c.descriptionText=()=> '';c.conciseEffectText=t=>String(t||'');c.projectIgnisEffectForActionItem=()=>null;c.inferPromptEffectText=()=>c.__effect||'';c.exactEffectContext=()=>({});c.effectSourceCode=()=>0;return c;};
      const out={};
      // F1: the Player's smart auto-pass keeps event windows (own attack damage step, own summon) but still passes pure phase windows.
      {const c=make();const honest={code:HONEST,controller:0,location:L.HAND,sequence:0};
       const win=(timing)=>({type:T.SELECT_CHAIN,player:0,forced:false,hint_timing:timing,selects:[honest]});
       out.damageStepAutoPass=!!c.smartOptionalChainResponse(win(H.DAMAGE_STEP|H.DAMAGE_CAL));
       out.summonWindowAutoPass=!!c.smartOptionalChainResponse(win(H.SUMMON));
       out.phaseWindowAutoPass=!!c.smartOptionalChainResponse(win(H.MAIN_END));
       out.chainEndAutoPass=!!c.smartOptionalChainResponse(win(H.CHAIN_END|H.TOGRAVE));
       out.noTimingAutoPass=!!c.smartOptionalChainResponse(win(0));}
      // F2: position changes are judged against the opponent's board.
      {const c=make();c.turnPlayer=1;const elfAtk={code:ELF,controller:1,location:L.MZONE,sequence:2,position:P.FACEUP_ATTACK};c.field.players[1].mzone[2]=elfAtk;
       c.field.players[0].mzone[0]={code:VORSE,controller:0,location:L.MZONE,sequence:0,position:P.FACEUP_ATTACK};
       out.elfToDefense=c.dummyPositionChangeScore(elfAtk);
       const elfDef={...elfAtk,position:P.FACEUP_DEFENSE};c.field.players[1].mzone[2]=elfDef;out.elfToAttack=c.dummyPositionChangeScore(elfDef);
       const skull={code:SKULL,controller:1,location:L.MZONE,sequence:3,position:P.FACEUP_DEFENSE};c.field.players[1].mzone[3]=skull;out.skullToAttack=c.dummyPositionChangeScore(skull);
       const bugSet={code:BUG,controller:1,location:L.MZONE,sequence:4,position:P.FACEDOWN_DEFENSE};c.field.players[1].mzone[4]=bugSet;out.bugFlip=c.dummyPositionChangeScore(bugSet);
       const elfSet={code:ELF,controller:1,location:L.MZONE,sequence:1,position:P.FACEDOWN_DEFENSE};c.field.players[1].mzone[1]=elfSet;out.elfFlip=c.dummyPositionChangeScore(elfSet);
       const idle=c.dummyIdleChoices({type:T.SELECT_IDLECMD,player:1,summons:[],monster_sets:[],special_summons:[],pos_changes:[elfDef,skull,bugSet,elfSet],spell_sets:[],activates:[],to_bp:true,to_ep:true});
       out.idlePosIndices=idle.filter(r=>r.action===I.SELECT_POS_CHANGE).map(r=>r.index);}
      // F3: LP-cost prompts are declined when they would leave the Dummy nearly dead.
      {const c=make();c.__effect='Pay 2000 LP; draw 2 cards.';c.lp=[8000,2500];out.payDeclined=c.dummyShouldAcceptYesNo({type:T.SELECT_EFFECTYN,player:1,code:0,controller:1});
       c.lp=[8000,8000];out.payAccepted=c.dummyShouldAcceptYesNo({type:T.SELECT_EFFECTYN,player:1,code:0,controller:1});}
      // F4: weak attackers do not ram into unknown set monsters; strong ones may.
      {const c=make();const setMonster={code:0,controller:0,location:L.MZONE,sequence:0,position:P.FACEDOWN_DEFENSE};
       out.weakIntoSet=c.dummyBattleTargetScore(800,setMonster);out.strongIntoSet=c.dummyBattleTargetScore(2500,setMonster);}
      return out;
    }''')
    browser.close()
print(result)
assert result['damageStepAutoPass'] is False and result['summonWindowAutoPass'] is False, result
assert result['phaseWindowAutoPass'] is True and result['chainEndAutoPass'] is True and result['noTimingAutoPass'] is True, result
assert result['elfToDefense']>0 and result['elfToAttack']<0 and result['skullToAttack']>0, result
assert result['bugFlip']>0 and result['elfFlip']<0, result
assert sorted(result['idlePosIndices'])==[1,2], result
assert result['payDeclined'] is False and result['payAccepted'] is True, result
assert result['weakIntoSet']<0 and result['strongIntoSet']>0, result
print('rc243 duel review regression passed')
