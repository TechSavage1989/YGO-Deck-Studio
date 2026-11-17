"""rc260: deck builder search. Scoring, typo tolerance, single-letter queries, hand trap tagging,
filters that work without choosing Card Type, sort defaults and the denser result grid."""
import os,re
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
app=(root/'web/js/app.js').read_text(encoding='utf-8')
css=(root/'web/styles.css').read_text(encoding='utf-8')
assert "duelcore.1-rc263" in app
start=app.index('// rc260: search scoring lives here');end=app.index('// rc260: end of search scoring helpers')
helpers=app[start:end]
# Source contracts for the parts that need the whole application to exercise.
assert "stats:(monster && type!=='Trap Monster') || !specific," in app
assert "state.filters.direction=['atk','def','level'].includes(mode)?'desc':'asc';" in app
assert "if (!hasQuery) return a.card.name.localeCompare(b.card.name) * dir;" in app
assert "for (let pass=0; pass<2 && !results.length; pass++) {" in app
assert "initShortcutHintToggles();" in app
for needle in ('.shortcut-strip.shortcut-strip-collapsed','.search-sort-mode-btn:not(.active)','.deck-sort-mode-btn:not(.active)','#searchResults.search-results.priority-layout-v4.grid-view { grid-template-columns:repeat(auto-fill,minmax(92px,1fr)) !important;'): assert needle in css,needle
stub='''
function normalizeSearchText(value=''){return String(value).normalize('NFKD').toLocaleLowerCase().replace(/[\\u0300-\\u036f]/g,'').replace(/&/g,' and ').replace(/[^a-z0-9]+/g,' ').trim().replace(/\\s+/g,' ');}
function cardEffectTags(card){return new Set(card.tags||[]);}
'''
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page();page.set_content('<!doctype html><html><body></body></html>')
    page.add_script_tag(content=stub+helpers+'\nwindow.T={prepareSearchQuery,deckSearchScore,searchEffectTags,searchEffectFiltersMatch};')
    r=page.evaluate('''()=>{
      const names=['Blue-Eyes White Dragon','Blue-Eyes Jet Dragon','Dark Magician','Dark Magician Girl','Ash Blossom & Joyous Spring','D/D/D Headhunt','D/D Dog','D.D. Dynamite','Sky Striker Ace - Raye','Mystical Space Typhoon','Pot of Greed'];
      const cards=names.map((name,i)=>({id:1000+i,name,archetype:'',desc:name==='Pot of Greed'?'Draw 2 cards.':''}));
      const run=(q,fuzzy=false)=>{const query=T.prepareSearchQuery(q);return cards.map(c=>[c.name,T.deckSearchScore(c,query,fuzzy)]).filter(x=>x[1]!=null).sort((a,b)=>a[1]-b[1]||a[0].length-b[0].length).map(x=>x[0])};
      const gamma={name:'PSY-Framegear Gamma',tags:['Special Summon']},other={name:'Dark Magician',tags:['Special Summon']};
      return{ddd:run('d/d/d'),ab:run('q x'),blue:run('blue eyes'),joined:run('blueeyes'),exact:run('dark magician'),id:run('1002'),text:run('draw 2 cards'),strictTypo:run('ash blosom'),typo:run('ash blosom',true),typo2:run('blu eyes wite dragon',true),typo3:run('dark magican',true),nonsense:run('xyzzy qqq',true),
        gamma:T.searchEffectFiltersMatch(gamma,new Set(['Hand Trap'])),other:T.searchEffectFiltersMatch(other,new Set(['Hand Trap'])),all:T.searchEffectFiltersMatch(gamma,new Set(['Hand Trap','Special Summon']),'All'),none:T.searchEffectFiltersMatch(other,new Set())};
    }''')
    browser.close()

assert r['ddd'][:1]==['D/D/D Headhunt'] and 'Blue-Eyes White Dragon' not in r['ddd'] and 'Dark Magician' not in r['ddd'],r['ddd']
assert r['ab']==[],r['ab']                                   # single letters alone match nothing
assert set(r['blue'])=={'Blue-Eyes White Dragon','Blue-Eyes Jet Dragon'} and set(r['joined'])==set(r['blue'])
assert r['exact'][:2]==['Dark Magician','Dark Magician Girl'],r['exact']
assert r['id']==['Dark Magician'] and r['text']==['Pot of Greed']
assert r['strictTypo']==[] and r['typo']==['Ash Blossom & Joyous Spring'],(r['strictTypo'],r['typo'])
assert r['typo2']==['Blue-Eyes White Dragon'],r['typo2']
assert r['typo3'][:1]==['Dark Magician'],r['typo3']
assert r['nonsense']==[]
assert r['gamma'] is True and r['other'] is False and r['all'] is True and r['none'] is True
print('rc260 deck builder search: scoring, typo tolerance, hand trap tagging and layout contracts passed')
