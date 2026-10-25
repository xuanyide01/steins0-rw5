from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1];p=R/'src/pages/index/index.ux'
# This one-time migration always starts from the preserved 0.1.0 UI, so rerunning
# it cannot duplicate newly added methods or imports.
source=(R/'reports/before-v011/index.ux').read_text('utf8');script=source.split('<script>',1)[1].split('</script>',1)[0]
def method(name,body):
    global script
    start=script.index('\n '+name+'(')
    match=re.search(r'\n [A-Za-z_$][\w$]*\(',script[start+2:])
    end=start+2+match.start() if match else script.index('\n};',start)
    script=script[:start]+'\n '+body.strip()+'\n'+script[end:]

script=script.replace("import {imagePath} from '../../common/assets.js';", "import {imagePath} from '../../common/assets.js';\nimport {FONT_SIZES,TEXT_MODES,settingsFrom,fontName,textModeName,pageLabel,sentenceStops} from '../../common/presentation.js';")
a=script.index(' private:');b=script.index('\n onInit()',a)
script=script[:a]+''' private:{mode:'title',loading:false,errorText:'',speaker:'',speakerFont:'sans-serif',bodyFont:'sans-serif',dateLabel:'',lines:[],dialogueHeight:140,fontSize:24,sceneImages:[],autoEnabled:false,phoneLabel:'手机',noticeColor:'#c7bcaf',mediaBusy:false,animationEnabled:true,zeroSrc:'/common/title-machine/atlas00.png',zeroLeft:0,heading:'',headingFont:'sans-serif',subtitle:'',subtitleFont:'sans-serif',panelCode:'SYSTEM',actions:[],actionsHeight:370,actionsTop:112,actionsViewport:382,listCode:'CHAPTER',pageLabel:'',rows:[],cardSrc:'',galleryPageLabel:'',galleryTop:[],galleryBottom:[],cgSrc:'',cgLabel:'',phoneHeading:'手机',phoneSub:'',phoneSubFont:'sans-serif',phonePageLabel:'',phoneHeight:322,phoneRows:[],phoneLines:[],phoneLeftLabel:'‹ 上一页',phoneBackLabel:'返回剧情',phoneRightLabel:'下一页 ›'},
'''+script[b:]

method('onInit',r'''onInit(){
  this._visible=true;this._seq=0;this._ui=0;this._cache=null;this._phoneSeq=0;this._slotSeq=0;this._gallerySeq=0;
  this._titleContext=true;this._settingsReady=false;this._progress={endings:{},rate:'1.129848'};this._settings=settingsFrom();this._galleryPage=0;this._routePage=0;
  this._auto=makeAutoClock(setTimeout,clearTimeout);
  this._music=makeTitleMusic(audio,(ok,busy)=>{this.mediaBusy=busy;this.syncMedia();});
  this._animation=makeTitleAnimation(setTimeout,clearTimeout,()=>this._visible&&this.mode==='title'&&this.animationEnabled&&!this.mediaBusy,(src,left)=>{this.zeroSrc=src;this.zeroLeft=left;});
  this.readJSON('/common/graph.txt',g=>{
   configure(g);this._graph=g;
   this.loadStorage('steins0_rw5_progress',raw=>{if(raw){try{const saved=JSON.parse(raw);this._progress={endings:saved.endings||{},rate:saved.rate||'1.129848'};}catch(e){}}});
   this.loadStorage('steins0_rw5_config',raw=>{let saved;try{saved=raw?JSON.parse(raw):null;}catch(e){}this._settings=settingsFrom(saved);this.fontSize=this._settings.font;this.animationEnabled=this._settings.animation;this._settingsReady=true;this.syncMedia();});
  });
 },''')
method('readJSON',r'''readJSON(uri,done,valid){file.readText({uri,complete:()=>{},success:r=>{if(valid&&!valid())return;try{done(JSON.parse(r.text));}catch(e){this.fail(e);}},fail:(d,c)=>{if(!valid||valid())this.fail('读取资源失败 '+uri+' / '+c);}});},''')
method('loadStorage',r'''loadStorage(key,done){storage.get({key,complete:()=>{},success:r=>done(r||''),fail:()=>done('')});},''')
method('writeStorage',r'''writeStorage(key,value,done){storage.set({key,value:JSON.stringify(value),complete:()=>{},success:()=>{if(done)done();},fail:(d,c)=>this.fail('保存失败 '+c)});},''')
method('syncMedia',r'''syncMedia(){if(!this._music||!this._animation)return;const allowed=this._settingsReady&&this._titleContext&&['title','extra','config','list','gallery','cg','overwrite'].indexOf(this.mode)>=0;this._music.update(!!(this._visible&&this._settings.sound&&allowed));this._animation.update();},''')
method('setMode',r'''setMode(mode){this.cancelReading();if(mode!=='play'&&this._noticeTimer){clearInterval(this._noticeTimer);this._noticeTimer=null;}if(mode!=='phone')this._phoneSeq++;this.mode=mode;console.log('STEINS0_RW5 mode '+mode);this.syncMedia();},''')
method('panel',r'''panel(mode,title,subtitle,actions){
  this.setMode(mode);this.panelCode={menu:'SYSTEM',config:'CONFIG',extra:'EXTRA',choice:'PHONE TRIGGER',end:'ENDING',overwrite:'SAVE DATA'}[mode]||'SYSTEM';
  this.heading=cleanText(title);this.headingFont=textFont(this.heading);this.subtitle=cleanText(subtitle||'');this.subtitleFont=textFont(this.subtitle);
  this.actionsTop=mode==='menu'?94:this.subtitle?122:112;this.actionsViewport=498-this.actionsTop;
  const height=mode==='menu'?44:53,uid=++this._ui;this._actions=actions;this.actionsHeight=Math.max(this.actionsViewport,actions.length*height);
  this.actions=actions.map((a,i)=>({key:uid+':'+i,text:cleanText(a.text),font:textFont(a.text),height,color:a.fn==='toTitle'?'#b1a39b':a.color||'#e3ded7'}));
  try{this.$element('actions-scroll').scrollTo({top:0,left:0,behavior:'instant'});}catch(e){}
 },''')
method('startNew',r'''startNew(){if(!this._graph)return;this._titleContext=false;this._seq++;this._cache=null;this._state=newState();Object.assign(this._state.endings,this._progress.endings);this.autoEnabled=false;this.present();},''')
method('startText',r'''startText(){
  this.setMode('play');this.drawScene();this._body=dialogueText(this._state.text);this.bodyFont=textFont(this._body);this._wrapped=wrapText(this._body,384,this.fontSize);
  this.dialogueHeight=Math.max(140,this._wrapped.split('\n').length*34+20);this._typed=0;this._scrollPaused=false;this._ignoreScrollUntil=Date.now()+400;
  try{this.$element('dialogue-scroll').scrollTo({top:0,left:0,behavior:'instant'});}catch(e){}
  const mode=this._settings.textMode;this._sentenceStops=sentenceStops(this._wrapped);this._sentenceIndex=0;
  if(mode==='instant'){this._typed=this._wrapped.length;this.paintText(this._wrapped);this.armAuto();return;}
  if(mode==='sentence'){this._typed=this._sentenceStops[0];this.paintText(this._wrapped.slice(0,this._typed));this.armAuto();return;}
  const token=this._typeGeneration,start=Date.now();this.paintText('');if(!this._visible)return;
  this._typeTimer=setInterval(()=>{if(token!==this._typeGeneration||this.mode!=='play'||!this._visible)return;this._typed=Math.min(this._wrapped.length,Math.floor((Date.now()-start)/30));this.paintText(this._wrapped.slice(0,this._typed));if(this._typed>=this._wrapped.length){clearInterval(this._typeTimer);this._typeTimer=null;this.armAuto();}},60);
  if(!this._wrapped.length){clearInterval(this._typeTimer);this._typeTimer=null;this.armAuto();}
 },''')
method('armAuto',r'''armAuto(){if(!this.autoEnabled||this._scrollPaused||this.mode!=='play'||!this._visible)return;let length=this._body.length;if(this._settings.textMode==='sentence'){const before=this._sentenceIndex?this._sentenceStops[this._sentenceIndex-1]:0;length=this._typed-before;}this._auto.arm(autoDelay(length,this._settings.autoSpeed),()=>this.autoEnabled&&this.mode==='play'&&this._visible&&!this._scrollPaused,()=>this.advance());},''')
method('advance',r'''advance(){
  if(this.mode!=='play'||this.loading)return;
  if(this._typeTimer){clearInterval(this._typeTimer);this._typeTimer=null;this._typed=this._wrapped.length;this.paintText(this._wrapped);this._scrollPaused=false;this.armAuto();return;}
  if(this._settings.textMode==='sentence'&&this._sentenceIndex<this._sentenceStops.length-1){this._sentenceIndex++;this._typed=this._sentenceStops[this._sentenceIndex];this.paintText(this._wrapped.slice(0,this._typed));this._scrollPaused=false;this.armAuto();return;}
  this._scrollPaused=false;try{next(this._state);this.present();}catch(e){this.fail(e);}
 },''')
method('touchStart',r'''touchStart(e){const t=e.touches&&e.touches.length?e.touches[0]:e;this._touchY=typeof t.localY==='number'?t.localY:typeof t.y==='number'?t.y:0;},''')
method('touchMove',r'''touchMove(e){const t=e.touches&&e.touches.length?e.touches[0]:e,y=typeof t.localY==='number'?t.localY:typeof t.y==='number'?t.y:this._touchY;if(Math.abs(y-this._touchY)>6){this._dragUntil=Date.now()+400;this._scrollPaused=true;this._auto.cancel();}},''')
method('scrolled',r'''scrolled(){if(Date.now()<(this._ignoreScrollUntil||0))return;this._dragUntil=Date.now()+400;this._scrollPaused=true;this._auto.cancel();},''')
method('showMenu',r'''showMenu(){if(!this._state)return;this.panel('menu','阅读菜单','',[
  {text:'保存进度',fn:'saveGame'},{text:'读取进度',fn:'loadGame'},{text:'下一章 ›',fn:'skipChapter'},
  {text:'自动播放：'+(this.autoEnabled?'开启':'关闭'),fn:'toggleAuto'},{text:'自动速度：'+['慢速','标准','快速'][this._settings.autoSpeed],fn:'toggleAutoSpeed'},
  {text:'文字显示：'+textModeName(this._settings.textMode),fn:'toggleTextMode'},{text:'字号：'+fontName(this.fontSize),fn:'toggleFont'},
  {text:'返回游戏',fn:'resume'},{text:'返回标题',fn:'toTitle'}]);},''')
method('toggleFont',r'''toggleFont(){this.fontSize=FONT_SIZES[(FONT_SIZES.indexOf(this.fontSize)+1)%FONT_SIZES.length];this._settings.font=this.fontSize;this.saveSettings();this.mode==='config'?this.openConfig():this.showMenu();},
 toggleTextMode(){this._settings.textMode=TEXT_MODES[(TEXT_MODES.indexOf(this._settings.textMode)+1)%TEXT_MODES.length];this.saveSettings();this.mode==='config'?this.openConfig():this.showMenu();},''')
method('toggleSound',r'''toggleSound(){this._settings.sound=!this._settings.sound;if(this._settings.sound)this._music.retry();this.saveSettings();this.openConfig();},''')
method('openConfig',r'''openConfig(){this.panel('config','设置','',[
  {text:'文字显示：'+textModeName(this._settings.textMode),fn:'toggleTextMode'},{text:'字号：'+fontName(this.fontSize),fn:'toggleFont'},
  {text:'自动速度：'+['慢速','标准','快速'][this._settings.autoSpeed],fn:'toggleAutoSpeed'},{text:'游戏音量：'+(this._settings.sound?'开启':'关闭'),fn:'toggleSound'},
  {text:'标题动画：'+(this.animationEnabled?'开启':'关闭'),fn:'toggleAnimation'},{text:'返回标题',fn:'toTitle'}]);},''')
method('openExtra',r'''openExtra(){this.panel('extra','扩展','',[{text:'CG 鉴赏',fn:'openGallery'},{text:'选择路线与章节',fn:'openRoutes'},{text:'通关记录',fn:'openEndings'},{text:'返回标题',fn:'toTitle'}]);},''')
method('toTitle',r'''toTitle(){this._seq++;this._slotSeq++;this._gallerySeq++;this.autoEnabled=false;this._cache=null;this._state=null;this._phoneCache=null;this.sceneImages=[];this.lines=[];this.phoneLines=[];this.phoneRows=[];this.rows=[];this._titleContext=true;this.loading=false;this.setMode('title');},''')
method('renderList',r'''renderList(){
  const l=this._list,uid=++this._ui,pages=Math.max(1,Math.ceil(l.items.length/4));l.page=Math.max(0,Math.min(pages-1,l.page));this.setMode('list');
  this.listCode={slots:this._slotKind==='save'?'SAVE':'LOAD',routes:'CHAPTER SELECT',chapters:'CHAPTER SELECT',endings:'CLEAR LIST'}[l.kind]||'SYSTEM';
  this.heading=cleanText(l.title);this.headingFont=textFont(this.heading);this.subtitle=cleanText(l.subtitle||'');this.subtitleFont=textFont(this.subtitle);this.pageLabel=pageLabel(l.page,pages);
  console.log('STEINS0_RW5 list '+l.kind+' '+l.page);this._pageItems=l.items.slice(l.page*4,l.page*4+4);
  this.rows=this._pageItems.map((x,i)=>({key:l.kind+':'+uid+':'+i,text:cleanText(x.text),font:textFont(x.text),meta:cleanText(x.meta||''),metaFont:textFont(x.meta||''),preview:cleanText(x.preview||'').slice(0,20),previewFont:textFont(x.preview||'')}));
 },''')
method('previousPage',r'''previousPage(){if(this._list.page<=0)return;this._list.page--;this.renderList();if(this._list.kind==='slots')this.loadSlotPage();},
 nextPage(){if(this._list.page>=Math.ceil(this._list.items.length/4)-1)return;this._list.page++;this.renderList();if(this._list.kind==='slots')this.loadSlotPage();},
 listBack(){const fn=this._list.back||'openExtra';if(typeof this[fn]==='function')this[fn]();},''')
method('openSlots',r'''openSlots(kind){if(!this._graph)return;const back=this._titleContext?'toTitle':'showMenu';this._slotKind=kind;this._slotData={};this._slotSeq++;this.list('slots',kind==='save'?'选择保存栏位':'选择读取栏位','共 30 个栏位',Array.from({length:30},(_,i)=>({text:'存档 '+('0'+(i+1)).slice(-2),meta:'读取中…',fn:'selectSlot',value:i})),back);this.loadSlotPage();},''')
method('loadSlotPage',r'''loadSlotPage(){const l=this._list,page=l.page,seq=this._slotSeq;for(let i=page*4;i<Math.min(page*4+4,30);i++)this.loadStorage(slotKey(i),raw=>{if(seq!==this._slotSeq||this._list!==l)return;let saved=null;try{saved=decodeSlotMeta(raw);}catch(e){saved={invalid:true};}this._slotData[i]={raw,saved};const row=slotRow(i,saved);l.items[i]={text:row.title,meta:row.meta.slice(0,62),preview:row.preview,fn:'selectSlot',value:i};if(this.mode==='list'&&this._list===l&&l.page===page)this.renderList();});},''')
script=script.replace("this._state=save.state;Object.assign", "this._titleContext=false;this._state=save.state;Object.assign")
method('openRoutes',r'''openRoutes(){this.list('routes','选择路线与章节','',this._graph.titles.map((text,i)=>({text,meta:'点击选择章节',fn:'openChapters',value:i})),'openExtra');this._list.page=this._routePage||0;this.renderList();},''')
method('openChapters',r'''openChapters(group){this._routePage=Math.floor(group/4);this._browseGroup=group;const chapters=Object.keys(this._graph.starts).map(k=>this._graph.starts[k]).filter(x=>x.group===group).sort((a,b)=>a.script-b.script);this.list('chapters','选择章节',this._graph.titles[group],chapters.map((x,i)=>({text:storyDate({date:x.date}),meta:'第 '+(i+1)+' 节',fn:'startChapter',value:x})),'openRoutes');},''')
method('startChapter',r'''startChapter(item){this._titleContext=false;this._cache=null;this._state=newChapterState(item);Object.assign(this._state.endings,this._progress.endings);this.autoEnabled=false;this.present();},''')
method('openGallery',r'''openGallery(){if(this._gallery){this.galleryList();return;}const seq=++this._gallerySeq;this.loading=true;this.readJSON('/common/gallery.txt',g=>{this.loading=false;this._gallery=g;this._galleryTotal=g.reduce((n,x)=>n+x.images.length,0);this.galleryList();},()=>seq===this._gallerySeq);},''')
method('galleryList',r'''galleryList(){
  this.setMode('gallery');const pages=Math.max(1,Math.ceil(this._gallery.length/4));this._galleryPage=Math.max(0,Math.min(pages-1,this._galleryPage));
  const start=this._galleryPage*4,uid=++this._ui,items=this._gallery.slice(start,start+4).map((g,i)=>({key:uid+':'+(start+i),index:start+i,src:imagePath(g.images[0]),label:'CG '+('00'+(start+i+1)).slice(-3),count:g.images.length+' 张'+(g.images.length>1?'差分':'')}));
  this.galleryTop=items.slice(0,2);this.galleryBottom=items.slice(2,4);this.galleryPageLabel=this._gallery.length+' 组 · '+(this._galleryTotal||this._gallery.reduce((n,g)=>n+g.images.length,0))+' 张\n'+pageLabel(this._galleryPage,pages);
  console.log('STEINS0_RW5 gallery '+this._galleryPage+' '+items.length);
 },
 previousGalleryPage(){if(this._galleryPage<=0)return;this._galleryPage--;this.galleryList();},
 nextGalleryPage(){if(this._galleryPage>=Math.ceil(this._gallery.length/4)-1)return;this._galleryPage++;this.galleryList();},''')
method('viewCg',r'''viewCg(i){if(!this._gallery||i<0||i>=this._gallery.length)return;this._cgIndex=i;this._cgVariant=0;this.drawCg();},
 drawCg(){this.setMode('cg');const g=this._gallery[this._cgIndex];this.cgSrc=imagePath(g.images[this._cgVariant]);this.cgLabel='CG '+('00'+(this._cgIndex+1)).slice(-3)+(g.images.length>1?' · 第 '+(this._cgVariant+1)+' 张，共 '+g.images.length+' 张 · 点击切换':'');console.log('STEINS0_RW5 cg '+this._cgIndex+' '+this._cgVariant);},
 cycleCg(){if(this.mode!=='cg'||this._gallery[this._cgIndex].images.length<2)return;this._cgVariant=(this._cgVariant+1)%this._gallery[this._cgIndex].images.length;this.drawCg();},
 previousCg(){if(this._cgIndex>0)this.viewCg(this._cgIndex-1);},
 nextCg(){if(this._cgIndex<this._gallery.length-1)this.viewCg(this._cgIndex+1);},
 galleryBack(){this._galleryPage=Math.floor(this._cgIndex/4);this.galleryList();},''')

# Phone implementation is kept in a separate readable patch source.
start=script.index('\n refreshNotice(');end=script.index('\n};',start)
script=script[:start]+'\n'+(R/'tools/phone-v011.methods').read_text('utf8').strip()+'\n'+script[end:]

template=(R/'tools/ui-v011.template').read_text('utf8');style=(R/'tools/ui-v011.style').read_text('utf8')
p.write_text(template+'\n<script>\n'+script.strip()+'\n</script>\n'+style,encoding='utf-8')
for name in ['src/manifest.json','src/config-watch.json','package.json']:
    f=R/name;x=json.loads(f.read_text('utf8'))
    if name=='package.json':x['version']='0.1.1'
    else:x['versionName']='0.1.1';x['versionCode']=5
    f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
