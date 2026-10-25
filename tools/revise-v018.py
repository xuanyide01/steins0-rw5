from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v018'
for rel in ['src/pages/index/index.ux','src/common/engine.js','src/common/title-music.js','src/common/media.txt','package.json','src/manifest.json','src/config-watch.json']:
    p=B/rel
    if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/rel,p)
m=json.loads((R/'reports/opening-v018-source.json').read_text('utf8'));assert m['frameSize']==[256,144]
reference=(R.parent/'steins-rw5-rebuild/src/common/opening.js').read_text('utf8')
reference=reference.replace('114583.15',str(m['durationMilliseconds'])).replace('1375',str(m['targetFrames'])).replace('83.3332',str(1000/12)).replace("s.cursor===557",'s.cursor===934').replace('MAIN00 movie 32','SG0_00_04 movie cue')
(R/'src/common/opening.js').write_text(reference,encoding='utf8')
p=R/'src/common/title-music.js';s=(B/'src/common/title-music.js').read_text('utf8')
s=s.replace('114.625',str(round(m['durationMilliseconds']/1000+.1,6)))
at=s.index('  stop,retry()')
s=s[:at]+"  playOpening(offset){stop();if(failed||!audio||destroyed)return;try{track='opening';seek=Math.max(0,offset||0)/1000;console.log('STEINS0_RW5 audio track opening');audio.autoplay=false;audio.loop=false;audio.src='/common/opening/op.mp3';owned=true;audio.play();if(seek>0)audio.currentTime=seek;}catch(e){fail(String(e));}},\n"+s[at:]
p.write_text(s,encoding='utf8')
p=R/'src/common/engine.js';s=(B/'src/common/engine.js').read_text('utf8')
s=s.replace('lastCard:-1};','lastCard:-1,openingDone:!!(id&&id!==graph.initial)||Number(cursor)>=934};')
s=s.replace('let order=state.mailSequence||0;',"if(typeof saved.openingDone!=='boolean')state.openingDone=state.chapter!==graph.initial||state.cursor>=934;let order=state.mailSequence||0;")
p.write_text(s,encoding='utf8')
p=R/'src/pages/index/index.ux';s=(B/'src/pages/index/index.ux').read_text('utf8')
s=s.replace('  <div if="{{mode === \'title\'}}"', '''  <div if="{{mode === 'opening'}}" class="opening-page" onclick="skipOpening"><div class="opening-viewport"><image class="opening-sheet" src="{{openingSrc}}" style="left:{{openingLeft}}px;top:{{openingTop}}px;" oncomplete="openingLoaded" onerror="openingError"></image></div></div>
  <div if="{{mode === 'title'}}"''',1)
s=s.replace("import {makeTitleAnimation}","import {wantsOpening,makeOpeningClock} from '../../common/opening.js';\nimport {makeTitleAnimation}")
s=s.replace("private:{mode:","private:{openingSrc:'',openingLeft:0,openingTop:0,mode:",1)
s=s.replace("this._auto=makeAutoClock(setTimeout,clearTimeout);", "this._auto=makeAutoClock(setTimeout,clearTimeout);\n  this._openingReturn='story';this._openingReady=false;this._openingRunning=false;this._openingPlayer=makeOpeningClock(setTimeout,clearTimeout,()=>Date.now(),(src,left,top)=>{this.openingSrc=src;this.openingLeft=left;this.openingTop=top;},()=>this.finishOpening('ended'));",1)
s=s.replace("onShow(){this._visible=true;this.armStartup();", "onShow(){this._visible=true;this.armStartup();if(this.mode==='opening'){this.resumeOpening();return;}")
s=s.replace("onHide(){this._visible=false;", "onHide(){this._visible=false;this.pauseOpening();")
s=s.replace("onDestroy(){this._destroyed=true;", "onDestroy(){this._destroyed=true;this.pauseOpening();this._openingPlayer.stop();")
s=s.replace("if(!this._music||!this._animation||this._destroyed)return;", "if(!this._music||!this._animation||this._destroyed)return;if(this.mode==='opening'){this.titleAnimationVisible=false;this._animation.stop();return;}")
s=s.replace("this.drawScene();if(this._state.lastCard!==this._state.group)", "if(wantsOpening(this._state)){this._openingReturn='story';this.startOpening();return;}this.drawScene();if(this._state.lastCard!==this._state.group)",1)
s=s.replace("{text:'通关记录',fn:'openEndings'}", "{text:'OP MOVIE / 观看 OP',fn:'watchOpening'},{text:'通关记录',fn:'openEndings'}")
at=s.index(' finishGame(){')
s=s[:at]+''' watchOpening(){if(this.mode!=='extra'||this.loading)return;this._openingReturn='extra';this.startOpening();},
 startOpening(){
  this.cancelReading();this._music.stop();this._animation.stop();this._cache=null;this.sceneImages=[];this._sceneSignature='';this.lines=[];this._wrapped='';this._body='';this.phoneRows=[];this.phoneLines=[];this.amadeusVisible=false;
  this.loading=false;this._openingReady=false;this._openingRunning=false;this.setMode('opening');this._openingPlayer.reset();this.resumeOpening();console.log('STEINS0_RW5 opening start '+this._openingReturn);
 },
 pauseOpening(){if(this._openingPlayer)this._openingPlayer.pause();this._openingRunning=false;if(this._openingLoadTimer)clearTimeout(this._openingLoadTimer);this._openingLoadTimer=null;},
 resumeOpening(){
  if(this.mode!=='opening'||!this._visible||this._destroyed||this._openingRunning)return;
  if(!this._openingReady){if(this._openingLoadTimer)clearTimeout(this._openingLoadTimer);this._openingLoadTimer=setTimeout(()=>this.openingError(),10000);return;}
  if(this._settings.sound)this._music.playOpening(this._openingPlayer.position());this._openingRunning=true;this._openingPlayer.resume();
 },
 openingLoaded(){if(this.mode!=='opening'||this._openingReady)return;this._openingReady=true;if(this._openingLoadTimer)clearTimeout(this._openingLoadTimer);this._openingLoadTimer=null;this.resumeOpening();console.log('STEINS0_RW5 opening playing');},
 openingError(){if(this.mode!=='opening')return;console.log('STEINS0_RW5 opening unavailable; continue safely');prompt.showToast({message:'OP暂时无法播放，已略过'});this.finishOpening('unavailable');},
 skipOpening(){if(this.mode==='opening')this.finishOpening('skipped');},
 finishOpening(reason){
  if(this.mode!=='opening')return;this.pauseOpening();this._openingPlayer.stop();this._music.stop();this.openingSrc='';this.mode='boot';console.log('STEINS0_RW5 opening complete '+reason+' '+this._openingReturn);
  if(this._openingReturn==='extra'){this._openingReturn='story';this.openExtra();}else{this._state.openingDone=true;this.present();}
 },
'''+s[at:]
s=s.replace('</style>', '''.opening-page{position:absolute;left:0px;top:0px;width:432px;height:514px;background-color:#000000;}
.opening-viewport{position:absolute;left:24px;top:149px;width:384px;height:216px;overflow:hidden;}
.opening-sheet{position:absolute;top:0px;width:1536px;height:432px;object-fit:contain;}
</style>''')
p.write_text(s,encoding='utf8')
for rel in ['src/manifest.json','src/config-watch.json','package.json']:
    p=R/rel;v=json.loads(p.read_text('utf8'))
    if 'version' in v:v['version']='0.1.8'
    else:v.update(versionName='0.1.8',versionCode=12)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=R/'src/common/media.txt';meta=json.loads(p.read_text('utf8'));meta.update(openingEnabled=True,openingDeferredByUser=False,openingDurationMs=m['durationMilliseconds'],openingFPS=12,openingFrames=m['targetFrames'],openingCue={'node':'n0','cursor':934},standaloneVideoExported=False);p.write_text(json.dumps(meta,separators=(',',':')),encoding='utf8')
print('v0.1.8 OP enabled at n0:934, independent EXTRA playback')
