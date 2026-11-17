"""rc261: replay review. A decision loop replaced by a seek or restart must not record or send its
answer, and a replay that has reached the end reads as finished with Play restarting it."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
core=(root/'web/js/duel-core.js').read_text(encoding='utf-8')
assert "duelcore.1-rc262" in core
# The guard sits directly after the player's answer is awaited, before anything is recorded.
answer=core.index("response=await this.playerResponse(prompt,{manualOnly:branchManual});")
guard=core.index("if (!this.running || !this.handle || loopSerial!==this.processLoopSerial) return;",answer)
record=core.index("this.recordReplayDecision(prompt,response);",answer)
assert answer<guard<record and guard-answer<700
assert core.count("response=await this.playerResponse(prompt,{manualOnly:true});\n        if(!this.running||!this.handle||loopSerial!==this.processLoopSerial)return;")==1
js=core.replace('export function ','function ').replace('export class ','class ')+'\nwindow.IntegratedDuelController=IntegratedDuelController;'
html='<!doctype html><html><body><input id="duelReplayTimeline" type="range"><span id="duelReplayTimelineValue"></span><span id="duelReplayStatus"></span><button id="duelReplayPlayPauseBtn"></button><select id="duelReplaySpeed"><option value="1">1</option></select></body></html>'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get("YGO_CHROMIUM_EXECUTABLE"),headless=True,args=['--no-sandbox'])
    page=browser.new_page();page.set_content(html);page.add_script_tag(content=js)
    r=page.evaluate('''()=>{
      const c=Object.create(window.IntegratedDuelController.prototype);const data={decisions:[{},{},{}],events:[]};
      Object.assign(c,{replaySpeed:1,replayPlayback:{mode:'playback',data,index:3,paused:false,seeking:false},running:false,starting:false,finalResult:{player:0,reason:1},liveReplayBranch:null,replaySession:null});
      const text=()=>[document.getElementById('duelReplayStatus').textContent,document.getElementById('duelReplayPlayPauseBtn').textContent];
      const out={};c.syncReplayControls();out.ended=[c.replayPlaybackEnded(),...text()];
      let restarted=0;c.replayFromStart=()=>{restarted++};c.toggleReplayPlayback();out.restarted=restarted;
      c.replayPlayback.index=2;c.running=true;c.finalResult=null;c.syncReplayControls();out.playing=[c.replayPlaybackEnded(),...text()];
      c.releaseReplayGate=()=>{};c.toggleReplayPlayback();out.pausedAfterToggle=c.replayPlayback.paused;out.restartedAgain=restarted;c.syncReplayControls();out.paused=text();
      c.replayPlayback.index=3;c.replayPlayback.seeking=true;c.running=false;out.seekingNotEnded=c.replayPlaybackEnded();
      c.replayPlayback={mode:'resume',data,index:3,paused:false,seeking:false};out.resumeNotEnded=c.replayPlaybackEnded();
      return out}''')
    browser.close()
assert r['ended']==[True,'Replay finished · 3 / 3','Play'],r['ended']
assert r['restarted']==1
assert r['playing']==[False,'Replay playing · 2 / 3','Pause'],r['playing']
assert r['pausedAfterToggle'] is True and r['restartedAgain']==1 and r['paused']==['Replay paused · 2 / 3','Play'],r
assert r['seekingNotEnded'] is False and r['resumeNotEnded'] is False
print('rc261 replay: stale-loop guard and finished-replay state passed')
