const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const R=path.resolve(__dirname,'..'),src=path.join(R,'src'),root=path.join(src,'pages/index/index.ux');
const modules=new Map(),timers=new Map(),store=new Map(),logs=[],reads=[];let nextTimer=0,now=0,delayReads=false,pending=[];
const schedule=(fn,ms,repeat)=>{timers.set(++nextTimer,{fn,ms,at:now+ms,repeat});return nextTimer;};
const clear=id=>timers.delete(id);
function tick(ms){const end=now+ms;for(let guard=0;guard<10000;guard++){const entry=[...timers].filter(([,t])=>t.at<=end).sort((a,b)=>a[1].at-b[1].at)[0];if(!entry)break;const [id,t]=entry;now=t.at;if(t.repeat)t.at+=t.ms;else timers.delete(id);t.fn();if(guard===9999)throw Error('Timer guard');}now=end;}
const FakeDate=class extends Date{static now(){return now;}};
const globals={setTimeout:(fn,ms)=>schedule(fn,ms,false),clearTimeout:clear,setInterval:(fn,ms)=>schedule(fn,ms,true),clearInterval:clear,Date:FakeDate,console:{log:(...x)=>logs.push(x.join(' ')),error:(...x)=>logs.push(x.join(' '))}};
const system={
 '@system.file':{readText(o){reads.push(o.uri);const work=()=>{try{o.success({text:fs.readFileSync(path.join(src,o.uri),'utf8')});}catch(e){if(o.fail)o.fail(e.message,1);}if(o.complete)o.complete();};if(delayReads)pending.push(work);else work();}},
 '@system.storage':{get(o){o.success(store.get(o.key)||'');},set(o){store.set(o.key,o.value);if(o.success)o.success();}},
 '@system.audio':{play(){if(this.onplay)this.onplay();},stop(){if(this.onstop)this.onstop();}},
 '@system.prompt':{showToast(){}}
};
function load(file){
 file=path.resolve(file);if(modules.has(file))return modules.get(file);let source=fs.readFileSync(file,'utf8');if(file.endsWith('.ux'))source=source.split('<script>')[1].split('</script>')[0];const params={...globals};
 source=source.replace(/^import\s+(.*?)\s+from\s+['"]([^'"]+)['"];?\r?$/gm,(_,spec,ref)=>{const dep=ref.startsWith('@system.')?system[ref]:load(path.resolve(path.dirname(file),ref));if(spec.startsWith('{')){for(const name of spec.slice(1,-1).split(',').map(x=>x.trim()).filter(Boolean))params[name]=dep[name];}else params[spec.trim()]=dep;return '';});
 let tail;if(file.endsWith('.ux')){source=source.replace('export default','const definition=');tail='return definition;';}else{const names=[...source.matchAll(/export (?:const|function) (\w+)/g)].map(x=>x[1]);source=source.replace(/export /g,'');tail='return {'+names.join(',')+'};';}
 const result=Function(...Object.keys(params),source+'\n'+tail)(...Object.values(params));modules.set(file,result);return result;
}
const d=load(root),ui=Object.assign({},JSON.parse(JSON.stringify(d.private)),d),e=load(path.join(src,'common/engine.js')),text=load(path.join(src,'common/text-font.js')),presentation=load(path.join(src,'common/presentation.js'));
ui.$element=()=>({scrollTo(){}});store.set('steins0_rw5_config',JSON.stringify({font:26,textSpeed:0,sound:false,animation:false}));ui.onInit();
assert.equal(ui.fontSize,28);assert.equal(ui._settings.textMode,'instant');
ui.openConfig();assert.ok(ui.actions.some(x=>x.text==='字号：大'));ui.toggleFont();assert.equal(ui.fontSize,22);assert.ok(ui.actions.some(x=>x.text==='字号：小'));ui.toggleFont();assert.equal(ui.fontSize,24);assert.ok(ui.actions.some(x=>x.text==='字号：中'));
assert.deepEqual(presentation.sentenceStops('第一句。第二句！\n第三句？'),[4,9,13]);
assert.equal(text.cleanText('\ue100 \ue101 \ue2bf \ue102 \ue2be'),'\ue100\ue101，\ue102。');
assert.equal(text.cleanText('El Psy Kongroo'),'El Psy Kongroo');assert.equal(text.cleanText('L a b'),'Lab');assert.equal(text.cleanText('I am so sorry. And you?'),'I am so sorry. And you?');
assert.equal(text.cleanText('中文 Lab 中文'),'中文Lab中文');assert.equal(text.cleanText('“ 测试。 中文 ”'),'“测试。中文”');
const graph=e.getGraph();let sample=null;
for(const c of graph.nodes.n0.chunks){const chunk=JSON.parse(fs.readFileSync(path.join(src,'common/story',c.file)));for(let i=0;i<chunk.frames.length;i++){const frame=chunk.frames[i],clean=text.dialogueText(frame[1]);if(presentation.sentenceStops(clean).length>1){sample={frame,cursor:graph.nodes.n0.chunks.slice(0,graph.nodes.n0.chunks.indexOf(c)).reduce((a,x)=>a+x.count,0)+i};break;}}if(sample)break;}
assert.ok(sample,'A real multiple-sentence source paragraph is required');
function atSample(mode){ui._titleContext=false;ui._settings.textMode=mode;ui.autoEnabled=false;ui._state=e.newState('n0',true,sample.cursor);ui._state.lastCard=sample.frame[4];ui._cache=null;ui.present();assert.equal(ui.mode,'play');}
atSample('sentence');const first=ui._typed,sourceCursor=ui._state.cursor;assert.ok(first<ui._wrapped.length);ui.advance();assert.equal(ui._state.cursor,sourceCursor);assert.ok(ui._typed>first);while(ui._sentenceIndex<ui._sentenceStops.length-1)ui.advance();ui.advance();assert.equal(ui._state.cursor,sourceCursor+1);
atSample('instant');assert.equal(ui.lines.map(x=>x.text).join('\n'),ui._wrapped);assert.equal(ui._typeTimer,null);ui.advance();assert.equal(ui._state.cursor,sourceCursor+1);
atSample('character');assert.ok(ui._typeTimer);ui.advance();assert.equal(ui._state.cursor,sourceCursor);assert.equal(ui._typeTimer,null);ui.advance();assert.equal(ui._state.cursor,sourceCursor+1);
atSample('instant');ui._settings.autoSpeed=2;ui.autoEnabled=true;ui.armAuto();tick(3000);assert.ok(ui._state.cursor>sourceCursor);ui.showMenu();const paused=ui._state.cursor;tick(5000);assert.equal(ui._state.cursor,paused);assert.equal(ui.actions.length,9);assert.ok(ui.actions.some(x=>x.text.startsWith('文字显示：')));
ui.autoEnabled=false;ui.toTitle();ui.openGallery();assert.equal(ui.galleryTop.length,2);assert.equal(ui.galleryBottom.length,2);assert.equal(new Set(ui.galleryTop.concat(ui.galleryBottom).map(x=>x.src)).size,4);assert.ok(!/\//.test(ui.galleryPageLabel));
ui.viewCg(23);assert.ok(ui.cgLabel.includes('共 2 张'));const originalCg=ui.cgSrc;ui.cycleCg();assert.notEqual(ui.cgSrc,originalCg);ui.galleryBack();assert.equal(ui._galleryPage,5);assert.equal(ui.galleryTop[0].index,20);
ui.openRoutes();ui.openChapters(0);assert.equal(ui._list.kind,'chapters');ui.listBack();assert.equal(ui._list.kind,'routes');assert.equal(ui._list.page,0);assert.equal(ui.rows[0].text,text.cleanText(graph.titles[0]));assert.ok(!/\//.test(ui.pageLabel));
ui._titleContext=false;ui._state=e.newState('n0',true,591);ui._state.lastCard=0;ui.present();ui.showPhone();assert.equal(ui.phoneRows[0].text,'收信箱');assert.equal(ui.phoneRows[1].text,'已发送');assert.equal(ui.phoneRows[2].text,'联系人');ui.openInbox();assert.equal(ui._state.read.length,ui._state.inbox.length);
const active=ui._state.inbox.find(x=>!x.stamp&&Math.floor(x.id/256)*256===2560);assert.ok(active);ui.openMessage(active);assert.equal(ui.phoneLeftLabel,'回复');ui.replyMessage();assert.equal(ui._phoneSection,'reply');const sentBefore=ui._state.sent.length;ui.sendRine(0);assert.ok(ui._state.sent.length>sentBefore);assert.ok(ui.phoneLines.some(x=>x.text==='动画表情'));assert.ok(ui.phoneLines.some(x=>x.font==='sgoriginal'));assert.equal(ui._phoneSection,'detail');
const sticker=ui._state.inbox.find(x=>x.stamp);ui.openMessage(sticker);assert.ok(ui.phoneLines.some(x=>x.text==='动画表情'));assert.ok(!ui.phoneLines.some(x=>/表情 \d/.test(x.text)));
ui.openInbox();ui._phoneCache=null;delayReads=true;ui.openMessage(active);ui.showPhone();const visible=JSON.stringify(ui.phoneRows);for(const work of pending.splice(0))work();delayReads=false;assert.equal(ui._phoneSection,'home');assert.equal(JSON.stringify(ui.phoneRows),visible);assert.equal(ui.loading,false);
const critical=Object.entries(graph.nodes).find(([,n])=>n.choice&&n.choice.critical);ui._state=e.newState(critical[0],true,critical[1].count);ui.autoEnabled=true;ui.present();assert.equal(ui.mode,'choice');const choiceNode=ui._state.chapter;tick(10000);assert.equal(ui._state.chapter,choiceNode);assert.equal(ui.mode,'choice');
ui.onHide();assert.equal(ui._typeTimer,null);assert.equal(ui._auto.pending(),false);ui.onDestroy();assert.ok(!logs.some(x=>x.startsWith('STEINS0_RW5 error')));
const report={result:'passed',sourceSentence:sample.frame[5],threeFontSizesAndLegacyMigration:true,characterSentenceInstantAdvance:true,chineseSpacingAndEnglishWords:true,menuNineItems:true,fourGalleryGroupsPerPage:true,variantAndReturnPage:true,routeFirstPageRefresh:true,phoneInboxSentContacts:true,replyDisplaysOriginalConversation:true,animatedStampsAreText:true,staleAsyncMessageReadIgnored:true,autoPausesOnMenuAndCriticalChoice:true,backgroundTimersCancelled:true};
fs.writeFileSync(path.join(R,'reports/ui-v011-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
