import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
js_source=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
assert "duelcore.1-rc254" in js_source
# Cards in the duel carry an accessible name, not a hover tooltip that covers neighbouring cards.
assert "identity is known; card remains face-down on the field" not in js_source
assert ".title=this.cardName(item.code)" not in js_source and ".title=this.cardName(visible)" not in js_source
js=js_source.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page()
    page.set_content('<!doctype html><html><body></body></html>')
    page.add_script_tag(content=js)
    result=page.evaluate('''async()=>{
      const proto=window.IntegratedDuelController.prototype;
      const make=()=>{const c=Object.create(proto);Object.assign(c,{turn:3,actionPresentationSpeed:'normal',duelAnimationsEnabled:true});
        c.cardData=code=>({1:{attack:1500},2:{attack:3000},3:{attack:2300}})[code]||{};c.getCardById=code=>code===3?{type:'Link Effect Monster'}:{type:'Effect Monster'};
        c.heldRightPassResponse=()=>null;c.traceSession=()=>{};c.replayPromptSignature=()=>'';return c;};
      const c=make(),f=item=>c.presentationImportance(item);
      const out={
        dummyNormal:f({kind:'summon',player:1,code:1}),ownNormal:f({kind:'summon',player:0,code:1}),
        dummyBoss:f({kind:'special',player:1,code:2}),dummyLink:f({kind:'special',player:1,code:3}),ownBoss:f({kind:'special',player:0,code:2}),
      };
      const d=make();out.repeat=[1,2,3,4].map(()=>d.presentationImportance({kind:'activate',player:1,code:1}));
      d.turn=4;out.nextTurn=d.presentationImportance({kind:'activate',player:1,code:1});
      const item={kind:'activate',player:1,code:1};const first=d.presentationImportance(item);out.cached=first===d.presentationImportance(item)&&first===d.presentationImportance(item);
      out.chain=make().presentationImportance({kind:'activate',player:1,code:1,chainLink:2});
      out.noCode=make().presentationImportance({kind:'activate',player:1,code:0});
      // prompt barrier is capped
      const w=make(),waits=[];w.wait=ms=>{waits.push(ms);return Promise.resolve()};
      w.cardAnimationPresentationUntil=Date.now()+9000;await w.awaitCardAnimationForDecision({player:0});
      w.cardAnimationPresentationUntil=Date.now()+600;await w.awaitCardAnimationForDecision({player:0});
      w.actionPresentationSpeed='fast';w.cardAnimationPresentationUntil=Date.now()+9000;await w.awaitCardAnimationForDecision({player:0});
      w.cardAnimationPresentationUntil=Date.now()+9000;await w.awaitCardAnimationForDecision({player:1});
      out.waits=waits;return out;
    }''')
    browser.close()
print(result)
r=result
assert r['dummyNormal']==0.85 and r['ownNormal']<r['dummyNormal'] and r['dummyBoss']==1.15 and r['dummyLink']==1.15 and r['ownBoss']<r['dummyBoss'], r
assert r['repeat'][0]==1 and r['repeat'][1]==0.75 and r['repeat'][2]==0.6 and r['repeat'][3]==0.6 and r['nextTurn']==1, r
assert r['cached'] is True and r['chain']==1.05 and r['noCode']==1, r
assert all(0.55<=v<=1.25 for v in [r['dummyNormal'],r['ownNormal'],r['dummyBoss'],r['ownBoss'],*r['repeat']]), r
w=r['waits']
assert len(w)==3 and w[0]==2200 and 0<w[1]<=600 and w[2]==round(2200*0.72), w
print('rc248 pacing regression passed')
