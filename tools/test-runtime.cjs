const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
function moduleLoad(name){let s=fs.readFileSync(path.join(root,'src/common',name+'.js'),'utf8');const names=[...s.matchAll(/export (?:function|const) (\w+)/g)].map(x=>x[1]);s=s.replace(/^import .*;\r?\n/gm,'').replace(/export /g,'');return vm.runInNewContext(s+'\n;({'+names.join(',')+'})',{console,Number,Date,JSON,Object,Array,Error,Math});}
const e=moduleLoad('engine'),graph=read('src/common/graph.txt');e.configure(graph);
const recipe=(r,c)=>['TA','RMG','PR'].includes(r)&&c.source.script==='SG0_01_08'&&c.mode===18||['RMG','PR'].includes(r)&&c.source.script==='SG0_A02_08'||r==='PR'&&c.source.script==='SG0_A03_11'||r==='GS'&&c.source.script==='SG0_B01_11';
const results=[];
for(const route of ['TA','RMG','PR','GS','VA','TRUE']){
 let s=e.newState();if(route==='TRUE')s.endings[0]=true;let count=0,cache={},ending;
 for(let guard=0;guard<50000;guard++){
  const f=e.locate(s);
  if(f.type==='end'){ending=s.endingId;break;}
  if(f.type==='choice'){e.choose(s,f.items[recipe(route,f)?0:1],recipe(route,f)?0:1);continue;}
  const pending=e.phoneChoice(s);if(pending&&recipe(route,pending)){e.answerCall(s,true);continue;}
  const data=cache[f.file]||(cache={[f.file]:read('src/common/story/'+f.file)})[f.file];e.readFrame(data,s,f.base);count++;
  if(count%700===0){const saved=e.checkpoint(s);assert.equal(saved.history,undefined);s=e.restore(saved);}
  e.next(s);
 }
 assert.equal(ending,{TA:1,RMG:2,PR:0,GS:4,VA:3,TRUE:5}[route]);results.push({route,frames:count,ending});
}
// Every original critical decision must stop chapter skipping, and survive reload.
let critical=0,reply=0;
for(const [id,n] of Object.entries(graph.nodes)){
 if(n.choice&&n.choice.critical){let s=e.newState(id,true,n.count);const f=e.locate(s);assert.equal(f.type,'choice');s=e.restore(e.checkpoint(s));assert.equal(e.locate(s).type,'choice');e.nextChapter(s);assert.equal(e.locate(s).type,'choice');e.answerCall(s,true);assert.notEqual(s.chapter,id);critical++;}
 for(const event of n.events)if(event.type==='rineReply'){
  let s=e.newState(id,true,event.at);e.locate(s);const w=s.replyWindows.find(x=>x.base===event.base);if(!w)continue;
  const r=read('src/common/reply/'+event.key+'.txt');assert.ok(r.replies.length);const returned=e.sendReply(s,r,0);assert.ok(returned.length);assert.equal(s.replyWindows.some(x=>x.base===event.base),false);assert.throws(()=>e.sendReply(s,r,0));reply++;
 }
}
// Worldline reset clears prior RINE; inbox opening marks all visible messages read.
const resetNode=Object.entries(graph.nodes).find(([id,n])=>n.events.some(e=>e.type==='rineReset'&&e.scope==='history'));
assert.ok(resetNode);let s=e.newState(resetNode[0]);s.inbox=[{key:'old'}];s.sent=[{key:'sent'}];e.locate(s);const resetAt=resetNode[1].events.find(e=>e.type==='rineReset'&&e.scope==='history').at;s.cursor=resetAt;e.locate(s);assert.ok(!s.inbox.some(x=>x.key==='old'));e.markRead(s);assert.equal(s.read.length,s.inbox.length);
const displayNode=Object.entries(graph.nodes).find(([id,n])=>n.events.some(e=>e.type==='rineReset'&&e.scope==='display'));assert.ok(displayNode);s=e.newState(displayNode[0]);s.inbox=[{key:'past'}];s.sent=[{key:'reply'}];e.locate(s);assert.ok(s.inbox.some(m=>m.key==='past'));assert.ok(s.sent.some(m=>m.key==='reply'));
const report={status:'passed',results,criticalDecisions:critical,rineReplyFixtures:reply,saveRestoresDuringRoutes:true,originalVMOnWatch:false};
fs.writeFileSync(path.join(root,'reports/runtime-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
