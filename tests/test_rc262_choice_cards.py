"""rc262: cards offered in a selection show monster facts like the field (ATK/DEF, Level/Rank/Link,
Pendulum Scale, Link Arrows), and a selection prompt widened for its cards is not capped at 300px."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
core=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
css=(root/'web/duel-core.css').read_text(encoding='utf-8')
assert "duelcore.1-rc265" in core
assert "this.prompt.style.setProperty('max-width',`${measuredPromptWidth}px`,'important');" in core
assert "this.prompt.style.removeProperty('width');this.prompt.style.removeProperty('max-width');" in core
assert core.count("this.appendChoiceCardStats(")>=2
for needle in ('.duel-choice-stats{','.duel-choice-link-arrows>img.duel-choice-link-arrow.edge','.duel-choice-level.rank','container-type:inline-size'): assert needle in css,needle
js=core.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page();page.set_content('<!doctype html><html><head><style>'+css+'</style></head><body style="--duel-card-w:92px;--duel-card-h:134px"></body></html>');page.add_script_tag(content=js)
    r=page.evaluate('''()=>{
      const rows={1:{type:0x21,level:4,attack:1800,defense:1000,lscale:0,link_marker:0},2:{type:0x800021,level:4,attack:2500,defense:2000},3:{type:0x4000021,level:3,attack:2300,defense:0,link_marker:0x80|0x1|0x4},4:{type:0x1000021,level:7,attack:2500,defense:2000,lscale:4},5:{type:0x2,level:0},6:{type:0x21,level:4,attack:-2,defense:-2}};
      const c=Object.create(window.IntegratedDuelController.prototype);c.cardData=code=>rows[code]?{...rows[code]}:null;c.normalizeActionCode=x=>Number(x);
      c.monsterStatSnapshot=(code,info)=>info.live?{attack:2300,defense:1000,attackModified:true,defenseModified:false,progress:5,progressModified:true}:{};
      const out={};for(const code of [1,2,3,4,5,6,7]){const host=document.createElement('span');host.className='duel-prompt-card-art';document.body.append(host);c.appendChoiceCardStats(host,{code});out[code]={stats:host.dataset.choiceStats||'',chips:[...host.querySelectorAll('.duel-choice-level,.duel-choice-scale')].map(n=>n.textContent),on:[...host.querySelectorAll('.duel-choice-link-arrows>img.duel-choice-link-arrow.edge')].map(n=>n.className.split(' ')[1]),pos:[...host.querySelectorAll('.duel-choice-link-arrow')].map(n=>[n.className.split(' ')[1],n.style.left,n.style.top,n.style.getPropertyValue('--link-arrow-angle'),n.getAttribute('src')]),arrows:host.querySelectorAll('.duel-choice-link-arrow').length};}
      const live=document.createElement('span');live.className='duel-prompt-card-art';document.body.append(live);c.appendChoiceCardStats(live,{code:1,live:true});out.live={stats:live.dataset.choiceStats,mod:[...live.querySelectorAll('.modified')].map(n=>n.textContent)};
      const box=document.querySelector('.duel-prompt-card-art .duel-choice-stats').getBoundingClientRect(),art=document.querySelector('.duel-prompt-card-art');art.style.cssText='display:block;position:relative;width:92px;height:134px';const b2=art.querySelector('.duel-choice-stats').getBoundingClientRect();out.fits=b2.width<=92;return out}''')
    browser.close()
assert {k:v for k,v in r['1'].items() if k!='pos'}=={'stats':'ATK 1,800 DEF 1,000','chips':['Lv 4'],'on':[],'arrows':0},r['1']
assert r['2']['stats']=='ATK 2,500 DEF 2,000' and r['2']['chips']==['Rank 4'],r['2']
assert r['3']['stats']=='ATK 2,300 LINK-3' and r['3']['chips']==[] and sorted(p[0] for p in r['3']['pos'])==sorted(['t','bl','br']) and r['3']['arrows']==3,r['3']
assert r['4']['chips']==['Lv 7','Scale 4'],r['4']
assert all({k:v for k,v in r[k2].items() if k!='pos'}=={'stats':'','chips':[],'on':[],'arrows':0} for k2 in ('5','7'))   # Spell / unknown: nothing
assert r['6']['stats']=='ATK ? DEF ?',r['6']
assert r['live']['stats']=='ATK 2,300 DEF 1,000' and 'Lv 5' in r['live']['mod'] and '2300' in ''.join(r['live']['mod']),r['live']
assert r['fits'] is True
pos={p[0]:p[1:] for p in r['3']['pos']}
# rc264: centred on the arrows printed on Link card frames (measured on official card images)
assert pos['t']==['49.9%','16.8%','0deg','assets/link_arrow_up_red.png'] and pos['bl']==['11.2%','70.9%','180deg','assets/link_arrow_corner_red.png'] and pos['br']==['88.9%','70.7%','90deg','assets/link_arrow_corner_red.png'],pos
for needle in ('.duel-choice-link-arrows>img.duel-choice-link-arrow.edge{width:9.5%!important}','.duel-choice-link-arrows>img.duel-choice-link-arrow.corner{width:7%!important}','aspect-ratio:auto!important','top:74.5%'): assert needle in css,needle
print('rc262 choice-card stats and prompt width passed')
