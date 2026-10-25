const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const R=path.resolve(__dirname,'..'),src=path.join(R,'src/common'),g=JSON.parse(fs.readFileSync(path.join(src,'graph.txt'))),code=fs.readFileSync(path.join(src,'engine.js'),'utf8');const names=[...code.matchAll(/export function (\w+)/g)].map(x=>x[1]);const e=vm.runInNewContext(code.replace(/export /g,'')+';({'+names.join(',')+'})',{JSON,Math,Number,Object,Array,Date,Error});e.configure(g);
const frames={};for(const [id,n] of Object.entries(g.nodes))frames[id]=n.chunks.flatMap(c=>JSON.parse(fs.readFileSync(path.join(src,'story',c.file))).frames);
function slow(s){const initial=frames[s.chapter][s.cursor][4];for(let guard=0;guard<30000;guard++){const f=e.locate(s);if(f.type!=='text')return s;if(frames[s.chapter][s.cursor][4]!==initial)return s;const pending=e.phoneChoice(s),n=g.nodes[s.chapter];if(pending&&pending.critical&&n.events.some(x=>x.type==='closeChoice'&&x.at===s.cursor)){return s;}s.cursor++;}throw Error('reference guard');}
let tests=0;const stops=[];
for(const [id,n] of Object.entries(g.nodes)){
 const positions=[0,...n.chapters.slice(1).map(x=>Math.max(0,x[0]-1)),Math.max(0,n.count-1)];
 for(const pos of [...new Set(positions)]){
  if(pos>=n.count)continue;const a=e.newState(id,true,pos);e.locate(a);const b=e.restore(e.checkpoint(a));e.nextChapter(a);slow(b);assert.equal(a.chapter,b.chapter);assert.equal(a.cursor,b.cursor);assert.equal(e.locate(a).type,e.locate(b).type);tests++;
 }
 if(n.choice&&n.choice.critical){const s=e.newState(id,true,n.count);assert.equal(e.locate(s).type,'choice');const before=e.checkpoint(s);assert.equal(e.nextChapter(s),false);assert.equal(s.chapter,before.chapter);assert.equal(s.cursor,before.cursor);stops.push(id);}
}
let s=e.newState();e.locate(s);e.nextChapter(s);assert.equal(s.chapter,'n0');assert.equal(s.cursor,934);assert.equal(s.history.length,1);e.previous(s);assert.equal(s.cursor,0);
// Repeated jumps retain every route-critical decision rather than silently taking it.
for(const route of ['TA','RMG','PR','GS','VA','TRUE']){
 s=e.newState();if(route==='TRUE')s.endings[0]=true;let ended=false;
 for(let guard=0;guard<300;guard++){
  const f=e.locate(s);if(f.type==='end'){ended=true;assert.equal(s.endingId,{TA:1,RMG:2,PR:0,GS:4,VA:3,TRUE:5}[route]);break;}
  if(f.type==='choice'){const yes=['TA','RMG','PR'].includes(route)&&f.source.script==='SG0_01_08'&&f.mode===18||['RMG','PR'].includes(route)&&f.source.script==='SG0_A02_08'||route==='PR'&&f.source.script==='SG0_A03_11'||route==='GS'&&f.source.script==='SG0_B01_11';e.choose(s,f.items[yes?0:1],yes?0:1);}else e.nextChapter(s);
 }
 assert.ok(ended,route);
}
const report={result:'passed',slowFrameReferenceFixtures:tests,criticalChoicesProtected:stops.length,prologueSkipsToFirstChapterAt934:true,oneStepBackRestoresPreSkip:true,allSixEndingsReachableByChapterJumps:true};fs.writeFileSync(path.join(R,'reports/skip-tests-v016.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
