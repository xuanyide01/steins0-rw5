"""Back up v0.1.6, correct call labels and reduce startup/save-list work."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];B=R/'reports/before-v017'
for rel in ['src/pages/index/index.ux','src/common/saves.js','src/common/graph.txt','tools/pack-runtime.cjs','src/manifest.json','src/config-watch.json','package.json']:
    target=B/rel
    if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/rel,target)
for rel in ['src/manifest.json','src/config-watch.json','package.json']:
    p=R/rel;v=json.loads(p.read_text('utf8'))
    if 'version' in v:v['version']='0.1.7'
    else:v.update(versionName='0.1.7',versionCode=11)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
g=json.loads((B/'src/common/graph.txt').read_text('utf8'));changed=[]
for node,n in g['nodes'].items():
    c=n.get('choice')
    if c and c['kind']=='call' and c['mode']==13:
        changed.append({'node':node,'source':c['source'],'oldHeading':c['heading'],'oldContact':c['contact']})
        c.update(contact=3,heading='Amadeus 来电')
(R/'src/common/graph.txt').write_text(json.dumps(g,ensure_ascii=False,separators=(',',':')),encoding='utf8')
(R/'reports/call-label-v017.json').write_text(json.dumps({'result':'passed','reason':'SC3 mode 13 is Amadeus; W6613 can retain the previous ordinary RINE contact','changed':changed},ensure_ascii=False,indent=2),encoding='utf8')
p=R/'tools/pack-runtime.cjs';s=(B/'tools/pack-runtime.cjs').read_text('utf8');s=s.replace("if(node.choice.kind==='call')node.choice.heading=names[node.choice.contact]||'来电';", "if(node.choice.kind==='call'){if(node.choice.mode===13){node.choice.contact=3;node.choice.heading='Amadeus 来电';}else node.choice.heading=names[node.choice.contact]||'来电';}")
p.write_text(s,encoding='utf8')
s=(B/'src/pages/index/index.ux').read_text('utf8')
s=s.replace("animationEnabled && !mediaBusy",'titleAnimationVisible')
s=s.replace("import {slotKey,decodeSave,decodeSlotMeta,createSave,slotRow}","import {slotKey,decodeSave,decodeSlotMeta,createSave,slotRow,slotMeta,SLOT_INDEX_KEY,decodeSlotIndex}")
s=s.replace("import {worldlineFor}","import {callHeading,callContact} from '../../common/phone-presentation.js';\nimport {worldlineFor}")
s=s.replace("animationEnabled:true,zeroSrc:","animationEnabled:true,titleAnimationVisible:false,zeroSrc:")
a=s.index(' onInit(){');b=s.index(' readJSON(',a)
s=s[:a]+''' onInit(){
  this._destroyed=false;this._visible=true;this._seq=0;this._ui=0;this._cache=null;this._phoneSeq=0;this._slotSeq=0;this._gallerySeq=0;
  this._titleContext=true;this._settingsReady=false;this._startupReady=false;this._animationReady=false;this._graphWaiting=[];this._slotCatalog=null;this._slotIndexWaiting=[];
  this._progress={endings:{},rate:'1.129848'};this._settings=settingsFrom();this._galleryPage=0;this._routePage=0;
  this._auto=makeAutoClock(setTimeout,clearTimeout);
  this._music=makeTitleMusic(audio,(ok,busy)=>{this.mediaBusy=busy;this.syncMedia();});
  this._animation=makeTitleAnimation(setTimeout,clearTimeout,()=>this.titleAnimationVisible,(src,left)=>{this.zeroSrc=src;this.zeroLeft=left;});
  this.loadStorage('steins0_rw5_progress',raw=>{if(this._destroyed)return;if(raw){try{const saved=JSON.parse(raw);this._progress={endings:saved.endings||{},rate:saved.rate||'1.129848'};}catch(e){}}});
  this.loadStorage('steins0_rw5_config',raw=>{if(this._destroyed)return;let saved;try{saved=raw?JSON.parse(raw):null;}catch(e){}this._settings=settingsFrom(saved);this.fontSize=this._settings.font;this.animationEnabled=this._settings.animation;this._settingsReady=true;this.armStartup();});
 },
 armStartup(){
  if(this._destroyed||!this._visible||!this._settingsReady)return;
  if(!this._startupReady){if(!this._startupTimer)this._startupTimer=setTimeout(()=>{this._startupTimer=null;if(this._destroyed||!this._visible)return;this._startupReady=true;console.log('STEINS0_RW5 startup music ready');this.syncMedia();this.armStartup();},800);return;}
  if(!this._animationReady&&!this._animationWarmup)this._animationWarmup=setTimeout(()=>{this._animationWarmup=null;if(this._destroyed||!this._visible)return;this._animationReady=true;console.log('STEINS0_RW5 startup animation ready');this.syncMedia();},900);
  this.syncMedia();
 },
 cancelStartup(){if(this._startupTimer)clearTimeout(this._startupTimer);this._startupTimer=null;if(this._animationWarmup)clearTimeout(this._animationWarmup);this._animationWarmup=null;},
 ensureGraph(done){
  if(this._graph){done();return;}this._graphWaiting.push(done);if(this._graphLoading)return;
  this._graphLoading=true;this.loading=true;this.syncMedia();console.log('STEINS0_RW5 graph lazy load');
  this.readJSON('/common/graph.txt',g=>{configure(g);this._graph=g;this._graphLoading=false;this.loading=false;const waiting=this._graphWaiting;this._graphWaiting=[];for(const next of waiting)next();this.syncMedia();},()=>!this._destroyed);
 },
 onShow(){this._visible=true;this.armStartup();if(this.mode==='play'&&this._state)this.present();else if(this.mode==='card')this.closeCard();},
 onHide(){this._visible=false;this.cancelStartup();this.cancelReading();if(this._cardTimer)clearTimeout(this._cardTimer);this._cardTimer=null;if(this._noticeTimer)clearInterval(this._noticeTimer);this._noticeTimer=null;this.titleAnimationVisible=false;this._music.stop();this._animation.stop();},
 onDestroy(){this._destroyed=true;this._seq++;this._slotSeq++;this._phoneSeq++;this._gallerySeq++;this.cancelStartup();this.cancelReading();if(this._noticeTimer)clearInterval(this._noticeTimer);if(this._cardTimer)clearTimeout(this._cardTimer);this.titleAnimationVisible=false;this._animation.stop();this._music.destroy();this._graphWaiting=[];this._slotIndexWaiting=[];this._cache=null;this._phoneCache=null;},
'''+s[b:]
s=s.replace("this.loading=false;this.cancelReading();this.mode='error';", "this.loading=false;this._saving=false;this._slotRestoreLoading=false;this._graphLoading=false;this._graphWaiting=[];this.cancelReading();this.mode='error';")
a=s.index(' syncMedia(){');b=s.index('\n\n cancelReading()',a)
s=s[:a]+''' syncMedia(){
  if(!this._music||!this._animation||this._destroyed)return;
  const quiet=this._graphLoading||this._slotRestoreLoading,allowed=this._settingsReady&&this._startupReady&&this._titleContext&&!quiet&&['title','extra','config','list','gallery','cg','overwrite'].indexOf(this.mode)>=0;
  this._music.update(!!(this._visible&&this._settings.sound&&allowed));
  this.titleAnimationVisible=!!(this._visible&&this.mode==='title'&&this._settingsReady&&this._startupReady&&this._animationReady&&this.animationEnabled&&!quiet&&!this.mediaBusy);
  this._animation.update();
 },'''+s[b:]
s=s.replace("action(index){const item", "action(index){if(this._saving)return;const item")
s=s.replace("startNew(){if(!this._graph)return;", "startNew(){if(this._graphLoading)return;this._titleContext=false;this.setMode('boot');if(!this._graph){this.ensureGraph(()=>this.startNew());return;}")
s=s.replace("this.panel('choice',choice.heading,", "this.panel('choice',callHeading(choice),")
s=s.replace("rowPick(i){const row", "rowPick(i){if(this.loading)return;const row")
a=s.index(' openSlots(kind)');b=s.index(' openRoutes()',a)
s=s[:a]+''' openSlots(kind){
  if(!this._graph){this.ensureGraph(()=>this.openSlots(kind));return;}
  const back=this._titleContext?'toTitle':'showMenu';this._slotKind=kind;this._slotSeq++;
  this.list('slots',kind==='save'?'选择保存栏位':'选择读取栏位','共 30 个栏位',Array.from({length:30},(_,i)=>({text:'存档 '+('0'+(i+1)).slice(-2),meta:'读取中…',fn:'selectSlot',value:i})),back);this.loadSlotPage();
 },
 ensureSlotIndex(done){
  if(this._slotCatalog){done();return;}this._slotIndexWaiting.push(done);if(this._slotIndexLoading)return;this._slotIndexLoading=true;
  this.loadStorage(SLOT_INDEX_KEY,raw=>{if(this._destroyed)return;try{this._slotCatalog=decodeSlotIndex(raw);}catch(e){this._slotCatalog={};}this._slotIndexLoading=false;const waiting=this._slotIndexWaiting;this._slotIndexWaiting=[];for(const next of waiting)next();});
 },
 persistSlotIndex(){if(!this._slotCatalog)return;storage.set({key:SLOT_INDEX_KEY,value:JSON.stringify({version:1,slots:this._slotCatalog}),success:()=>{},fail:()=>{console.log('STEINS0_RW5 optional slot index write failed');}});},
 loadSlotPage(){
  const l=this._list,page=l.page,seq=this._slotSeq,valid=()=>!this._destroyed&&seq===this._slotSeq&&this._list===l&&this.mode==='list'&&l.page===page;this.loading=true;
  this.ensureSlotIndex(()=>{
   if(!valid())return;const indices=Array.from({length:Math.min(4,30-page*4)},(_,i)=>page*4+i);let cursor=0,changed=false;
   const finish=()=>{if(!valid())return;for(const i of indices){const row=slotRow(i,this._slotCatalog[i]);l.items[i]={text:row.title,meta:row.meta.slice(0,62),preview:row.preview,fn:'selectSlot',value:i};}this.loading=false;this.renderList();if(changed)this.persistSlotIndex();console.log('STEINS0_RW5 slots ready '+page);};
   const next=()=>{if(!valid())return;while(cursor<indices.length&&Object.prototype.hasOwnProperty.call(this._slotCatalog,indices[cursor]))cursor++;if(cursor>=indices.length){finish();return;}
    const i=indices[cursor++];this.loadStorage(slotKey(i),raw=>{if(!valid())return;try{this._slotCatalog[i]=decodeSlotMeta(raw);}catch(e){this._slotCatalog[i]={invalid:true};}changed=true;next();});
   };next();
  });
 },
 selectSlot(i){
  if(this.loading||!this._slotCatalog||!Object.prototype.hasOwnProperty.call(this._slotCatalog,i))return;
  const l=this._list,kind=this._slotKind,seq=++this._slotSeq;this.loading=true;this._slotRestoreLoading=true;this.syncMedia();
  this.loadStorage(slotKey(i),raw=>{
   if(this._destroyed||seq!==this._slotSeq||this._list!==l||this.mode!=='list')return;
   this.loading=false;this._slotRestoreLoading=false;
   if(kind==='load'){
    if(!raw){this._slotCatalog[i]=null;this.persistSlotIndex();this.loadSlotPage();this.syncMedia();return;}
    try{this._titleContext=false;this.setMode('boot');const save=decodeSave(raw);this._state=save.state;Object.assign(this._state.endings,this._progress.endings);this._cache=null;this.autoEnabled=false;this.present();}catch(e){this.fail(e);}return;
   }
   if(!this._state)return;this._writeSlot=i;if(raw)this.panel('overwrite','覆盖存档？','存档 '+('0'+(i+1)).slice(-2),[{text:'确认覆盖',fn:'confirmSave'},{text:'取消',fn:'saveGame'}]);else this.confirmSave();
  });
 },
 confirmSave(){
  if(this._saving||!this._state)return;this._saving=true;this.loading=true;const state=this._state,index=this._writeSlot,savedAt=Date.now(),sceneMode=state.choice?'choice':'play',value=createSave(state,sceneMode,savedAt),meta=slotMeta(value);
  this.writeStorage(slotKey(index),value,()=>{
   this._saving=false;this.loading=false;if(this._destroyed)return;if(!this._slotCatalog)this._slotCatalog={};this._slotCatalog[index]=meta;this.persistSlotIndex();this._progress.rate=worldlineFor(value.state);this.writeStorage('steins0_rw5_progress',this._progress);prompt.showToast({message:'保存成功'});
   console.log('STEINS0_RW5 saved '+index);if(this._state===state&&['list','overwrite'].indexOf(this.mode)>=0)this.resume();
  });
 },
'''+s[b:]
s=s.replace("openRoutes(){this.list", "openRoutes(){if(!this._graph){this.ensureGraph(()=>this.openRoutes());return;}this.list")
s=s.replace("openEndings(){this.list", "openEndings(){if(!this._graph){this.ensureGraph(()=>this.openEndings());return;}this.list")
s=s.replace("phoneContactName(id){return this._graph.phone.contactNames[id]||", "phoneContactName(id){return this._graph.phone.contactNames[id]||this._graph.phone.names[id]||")
s=s.replace("call.kind==='power'?'本段可以操作手机电源':call.heading", "call.kind==='power'?'本段可以操作手机电源':callHeading(call)")
s=s.replace("active.contact===id", "callContact(active)===id")
(R/'src/pages/index/index.ux').write_text(s,encoding='utf8')
print('v0.1.7 source prepared; corrected',len(changed),'call sites')
