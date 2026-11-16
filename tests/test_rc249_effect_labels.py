import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
js_source=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
assert "duelcore.1-rc260" in js_source
js=js_source.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1000,'height':700})
    page.set_content('<!doctype html><html><body><div id="side" style="position:fixed;left:0;top:0;width:100px;height:100px"></div><div id="board" style="position:absolute;left:200px;top:100px;width:600px;height:400px"></div><dialog id="art"><button id="inart">x</button></dialog></body></html>')
    page.add_script_tag(content=js)
    labels=page.evaluate('''()=>{
      const proto=window.IntegratedDuelController.prototype;const c=Object.create(proto);
      const gazelle=['If a "Salamangreat" monster is sent to your GY, except "Salamangreat Gazelle" (except during the Damage Step): You can Special Summon this card from your hand.','If this card is Normal or Special Summoned: You can send 1 "Salamangreat" card from your Deck to the GY, except "Salamangreat Gazelle".','You can only use each effect of "Salamangreat Gazelle" once per turn.'];
      const phoenix=['If this card is Link Summoned: You can discard 1 card, then target 1 Spell/Trap your opponent controls; destroy it, then, if this card was co-linked when this effect was activated, you can draw 1 card.','Co-linked monsters you control cannot be destroyed by battle.'];
      const twin=['Once per turn: You can target 1 monster; destroy it.','Once per turn: You can target 1 Spell; destroy it.'];
      c.getCardById=code=>code===7?{type:'Link Effect Monster'}:{type:'Effect Monster'};c.normalizeActionCode=proto.normalizeActionCode;
      return{special:c.matchShortEffectLabel('Special Summon',gazelle),send:c.matchShortEffectLabel('Send',gazelle),destroy:c.matchShortEffectLabel('Destroy',phoenix),
        tie:c.matchShortEffectLabel('Destroy',twin),hint:c.matchShortEffectLabel('Affected by "Mulcharmy Fuwalos"',gazelle),question:c.matchShortEffectLabel('Draw 1 card?',phoenix),unknown:c.matchShortEffectLabel('Frobnicate',gazelle),single:c.matchShortEffectLabel('Destroy',[phoenix[0]]),
        stripped:c.effectTextWithoutMaterials(7,'2 monsters with different names\\r\\nIf this card is Link Summoned: You can discard 1 card.'),kept:c.effectTextWithoutMaterials(1,'Line A\\nLine B')};
    }''')
    clicks=page.evaluate('''async()=>{
      const proto=window.IntegratedDuelController.prototype;const c=Object.create(proto);let closed=0;
      Object.assign(c,{boardWrap:document.getElementById('board'),prompt:null,promptView:'',cardDetailsOverlay:null});
      for(const name of ['hideCardHoverOverlay','hidePileHoverOverlay','captureDetailsReturnSnapshot','setLogCardFocus','populateBuilderDetails','toggleStyledText'])c[name]=()=>{};
      c.cardName=()=> 'Test Card';c.getCardTextStyling=()=>false;c.legalActionsForContext=()=>[];c.contextForCard=()=>null;
      c.button=(label,fn)=>{const b=document.createElement('button');b.textContent=label;b.addEventListener('click',fn);return b;};
      c.closeIndependentCardDetails=()=>{closed++;c.cardDetailsOverlay?.remove();c.cardDetailsOverlay=null;return true;};
      const open=async()=>{c.renderCardDetailsModal(123,{code:123});await new Promise(r=>setTimeout(r,30));};
      const isOpen=()=>!!document.querySelector('.duel-independent-card-details-overlay');const out={};
      await open();document.querySelector('.duel-independent-card-details-panel h2').click();out.insideKeeps=isOpen();
      document.getElementById('side').click();out.outsideCloses=!isOpen();
      await open();document.querySelector('.duel-independent-card-details-overlay').click();out.backdropCloses=!isOpen();
      await open();document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));out.escapeCloses=!isOpen();
      await open();document.dispatchEvent(new KeyboardEvent('keydown',{key:'a',bubbles:true}));out.otherKeyKeeps=isOpen();
      const art=document.getElementById('art');art.showModal();document.getElementById('inart').click();out.dialogClickKeeps=isOpen();
      document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));out.escapeWithDialogKeeps=isOpen();art.close();await new Promise(r=>setTimeout(r,30));
      document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));out.escapeRightAfterDialogKeeps=isOpen();
      await new Promise(r=>setTimeout(r,450));document.getElementById('side').click();out.finalOutsideCloses=!isOpen();out.closed=closed;
      // a closed window leaves no listeners behind that would close a later one early
      await open();await new Promise(r=>setTimeout(r,30));out.reopenStaysOpen=isOpen();return out;
    }''')
    browser.close()
print(labels);print(clicks)
assert labels['special'].endswith('You can Special Summon this card from your hand.') and labels['send'].startswith('If this card is Normal or Special Summoned'), labels
assert labels['destroy'].startswith('If this card is Link Summoned'), labels
assert labels['tie']=='' and labels['hint']=='' and labels['question']=='' and labels['unknown']=='' and labels['single']=='', labels
assert labels['stripped']=='If this card is Link Summoned: You can discard 1 card.' and labels['kept']=='Line A\nLine B', labels
for key in ('insideKeeps','outsideCloses','backdropCloses','escapeCloses','otherKeyKeeps','dialogClickKeeps','escapeWithDialogKeeps','escapeRightAfterDialogKeeps','finalOutsideCloses','reopenStaysOpen'): assert clicks[key] is True,(key,clicks)
assert clicks['closed']==4, clicks
print('rc249 effect label and Card Details dismissal regression passed')
